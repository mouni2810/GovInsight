"""
FastAPI Application for GovInsight

Provides REST API endpoints for querying Indian budget documents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
import sys
from pathlib import Path
import urllib.parse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag_pipeline import complete_query


# Initialize FastAPI app
app = FastAPI(
    title="GovInsight API",
    description="RAG-based API for querying Indian Union Budget documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PDF directory path
PDF_DIRECTORY = Path("data/raw_pdfs")


# Request models
class QueryFilters(BaseModel):
    """Optional filters for query"""
    year: Optional[str] = Field(None, description="Budget year (e.g., '2023-24')")
    ministry: Optional[str] = Field(None, description="Ministry name")
    scheme: Optional[str] = Field(None, description="Scheme name")
    top_k: Optional[int] = Field(7, ge=1, le=10, description="Number of chunks to retrieve")


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=1, description="User query about budget documents")
    filters: Optional[QueryFilters] = Field(None, description="Optional metadata filters")
    temperature: Optional[float] = Field(0.1, ge=0.0, le=1.0, description="LLM temperature")


class SourceDocument(BaseModel):
    """Source document metadata"""
    page_number: int
    year: str
    ministry: str
    document_name: Optional[str] = Field("", description="PDF filename for download")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str = Field(..., description="Generated answer with citations")
    sources: List[SourceDocument] = Field(..., description="Source documents used")
    num_chunks_used: int = Field(..., description="Number of chunks retrieved")
    query: str = Field(..., description="Original query")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# API endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to API info if HTML not found
        return """
        <html>
            <body>
                <h1>GovInsight API</h1>
                <p>Frontend not found. Please check if index.html exists.</p>
                <p>API Documentation: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "GovInsight API",
        "version": "1.0.0",
        "description": "RAG system for Indian Union Budget documents",
        "endpoints": {
            "/query": "POST - Query budget documents",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation",
            "/download/{filename}": "GET - Download source PDF"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GovInsight"
    }


@app.get("/download/{filename:path}")
async def download_pdf(filename: str):
    """
    Download a source PDF file.
    
    Args:
        filename: Name of the PDF file to download
        
    Returns:
        FileResponse with the PDF file
    """
    # Decode URL-encoded filename
    decoded_filename = urllib.parse.unquote(filename)
    
    # Security check: prevent directory traversal attacks
    if ".." in decoded_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Construct the full path
    pdf_path = PDF_DIRECTORY / decoded_filename
    
    # Check if file exists
    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found: {decoded_filename}"
        )
    
    # Return the file
    return FileResponse(
        path=str(pdf_path),
        filename=decoded_filename,
        media_type="application/pdf"
    )


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query Indian budget documents using RAG.
    
    Args:
        request: QueryRequest with query string and optional filters
        
    Returns:
        QueryResponse with answer, sources, and metadata
    """
    try:
        # Extract filters
        filters = request.filters or QueryFilters()
        
        # Execute RAG query
        print(f"[DEBUG] Executing query: {request.query}")
        result = complete_query(
            query=request.query,
            top_k=filters.top_k or 5,
            year=filters.year,
            ministry=filters.ministry,
            scheme=filters.scheme,
            temperature=request.temperature
        )
        print(f"[DEBUG] Result keys: {result.keys() if result else 'None'}")
        print(f"[DEBUG] Result: {result}")
        
        # Format sources - ensure sources list exists
        sources = []
        sources_list = result.get('sources', [])
        if sources_list is None:
            sources_list = []
        
        print(f"[DEBUG] Sources list: {sources_list}")
        
        for idx, source in enumerate(sources_list):
            print(f"[DEBUG] Processing source {idx}: {source}")
            # Ensure source is a dictionary
            if not isinstance(source, dict):
                print(f"[DEBUG] Skipping non-dict source: {source}")
                continue
            
            # Handle page_number - ensure it's always an int
            page_num = source.get('page_number', 0)
            if isinstance(page_num, str):
                if page_num == 'N/A' or page_num == '':
                    page_num = 0
                else:
                    try:
                        page_num = int(page_num)
                    except (ValueError, TypeError):
                        page_num = 0
            elif not isinstance(page_num, int):
                page_num = 0
            
            # Ensure year and ministry are always valid strings
            year = source.get('year', 'Unknown')
            if not year or year == '':
                year = 'Unknown'
            
            ministry = source.get('ministry', 'Unknown')
            if not ministry or ministry == '':
                ministry = 'Unknown'
            
            # Get document_name from metadata (already configured in metadata_config.py)
            document_name = source.get('document_name', '')
            
            print(f"[DEBUG] Creating SourceDocument: page={page_num}, year={year}, ministry={ministry}, doc={document_name}")
            sources.append(SourceDocument(
                page_number=page_num,
                year=str(year),
                ministry=str(ministry),
                document_name=str(document_name) if document_name else ''
            ))
        
        # Return response
        print(f"[DEBUG] Creating QueryResponse with {len(sources)} sources")
        return QueryResponse(
            answer=result['answer'],
            sources=sources,
            num_chunks_used=result['num_chunks_used'],
            query=request.query
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Vector store not found. Please run indexing first: {str(e)}"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    
    except KeyError as e:
        # Handle missing keys in response data
        import traceback
        missing_key = str(e).strip("'\"")
        tb = traceback.format_exc()
        print(f"KeyError traceback:\n{tb}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: Missing required field '{missing_key}' in response. Please re-index your documents with: python app/rag_pipeline.py --index --reset"
        )
    except Exception as e:
        import traceback
        error_details = str(e)
        tb = traceback.format_exc()
        print(f"Exception traceback:\n{tb}")
        # Include more context for debugging
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {error_details}. If this persists, try re-indexing: python app/rag_pipeline.py --index --reset"
        )


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

