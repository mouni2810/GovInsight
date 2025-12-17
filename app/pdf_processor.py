"""
PDF Processing Module for GovInsight

This module handles PDF loading, text extraction, and cleaning
for Indian government budget documents.

NOTE: Metadata is NOT extracted from PDF content or filenames.
All metadata must be manually configured in metadata_config.py
to ensure consistent and reliable metadata for the RAG pipeline.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
import tiktoken


class TokenChunker:
    """
    Token-based text chunker using tiktoken.
    
    Token-based chunking is preferred over character-based because:
    - Matches embedding model context windows
    - Consistent across languages/encodings
    - Better semantic boundaries
    """
    
    def __init__(self, model_name: str = "cl100k_base"):
        """
        Initialize the token chunker.
        
        Args:
            model_name: Tiktoken encoding name. 
                       "cl100k_base" is used by text-embedding-ada-002 and GPT-4
        """
        self.encoding = tiktoken.get_encoding(model_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def split_into_chunks(
        self, 
        text: str, 
        chunk_size: int = 300, 
        overlap: int = 75
    ) -> List[str]:
        """
        Split text into overlapping chunks based on token count.
        
        Args:
            text: Text to split
            chunk_size: Target tokens per chunk (default: 300)
            overlap: Token overlap between chunks (default: 75)
            
        Returns:
            List of text chunks
        """
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            
            # Decode the token slice back to text
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens).strip()
            
            if chunk_text:
                chunks.append(chunk_text)
            
            # Move forward by (chunk_size - overlap) tokens
            start += chunk_size - overlap
            
            # Prevent infinite loop if overlap >= chunk_size
            if start <= (end - chunk_size + overlap) and start < len(tokens):
                start = end - overlap
        
        return chunks


# Global token chunker instance (lazy initialization)
_token_chunker: TokenChunker = None


def _get_token_chunker() -> TokenChunker:
    """Get or create the global token chunker instance."""
    global _token_chunker
    if _token_chunker is None:
        _token_chunker = TokenChunker()
    return _token_chunker


class PDFProcessor:
    """
    Handles PDF text extraction and cleaning for budget documents.
    """
    
    def __init__(self, pdf_directory: str = "data/raw_pdfs"):
        """
        Initialize PDF processor.
        
        Args:
            pdf_directory: Path to directory containing PDF files
        """
        self.pdf_directory = Path(pdf_directory)
        if not self.pdf_directory.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")
    
    def load_pdfs(self) -> List[Path]:
        """
        Load all PDF files from the specified directory.
        
        Returns:
            List of PDF file paths
        """
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {self.pdf_directory}")
        return sorted(pdf_files)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """
        Extract text from a PDF file page by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries containing page text and metadata:
            [
                {
                    'page_number': int,
                    'text': str,
                    'document_name': str
                }
            ]
        """
        pages_data = []
        document_name = pdf_path.stem
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # Clean the extracted text
                cleaned_text = self._clean_text(text)
                
                if cleaned_text.strip():  # Only include pages with content
                    pages_data.append({
                        'page_number': page_num + 1,
                        'text': cleaned_text,
                        'document_name': document_name
                    })
            
            doc.close()
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return []
        
        return pages_data
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text while PRESERVING numerical data and budget figures.
        
        CRITICAL: Budget documents contain important numbers that must be preserved.
        Only remove true noise and formatting artifacts.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text with numbers preserved
        """
        # Remove excessive whitespace FIRST
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common header/footer patterns
        text = self._remove_headers_footers(text)
        
        # ONLY remove "Page X" style page numbers (very selective)
        # DO NOT remove standalone numbers - they could be budget figures!
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bpage\s+\d+\s+of\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove URLs (safe to remove)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove ONLY decorative elements (3+ repetitions for tables/borders)
        text = re.sub(r'\|{3,}', '', text)  # 3+ pipes (table borders)
        text = re.sub(r'-{5,}', '', text)   # 5+ dashes (horizontal lines)
        text = re.sub(r'_{5,}', '', text)   # 5+ underscores (underlines)
        
        # Final whitespace normalization
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """
        Remove common header and footer patterns from budget documents.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with headers/footers removed
        """
        # Common header/footer patterns in Indian budget documents
        patterns = [
            r'Ministry of Finance.*?Department of Economic Affairs',
            r'Government of India.*?Budget',
            r'Union Budget \d{4}-\d{2,4}',
            r'Printed by.*?Controller of Publications',
            r'Page \d+ of \d+',
            r'^\s*\d+\s*$',  # Standalone page numbers
            r'Source:.*?(?=\n|$)',
            r'Note:.*?(?=\n|$)',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text


def extract_text_from_single_pdf(pdf_path: str) -> List[Dict[str, any]]:
    """
    Utility function to extract text from a single PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of page dictionaries with text and metadata
    """
    processor = PDFProcessor()
    return processor.extract_text_from_pdf(Path(pdf_path))


def chunk_text_with_metadata(
    pages_data: List[Dict[str, any]],
    metadata: Dict[str, str],
    chunk_size: int = 300,
    overlap: int = 75
) -> List[Dict[str, any]]:
    """
    Chunk extracted text into smaller segments with complete metadata.
    
    This function splits page-level text into chunks of ~300 tokens
    with 75-token overlap to preserve context across chunk boundaries.
    Uses tiktoken for accurate token counting that matches embedding models.
    
    All metadata is passed in directly (not extracted from content) to ensure
    every chunk has complete and consistent metadata.
    
    Args:
        pages_data: List of page dictionaries from PDF extraction
        metadata: Complete metadata dictionary with all required fields:
                  - year: Budget year (e.g., "2023-24")
                  - ministry: Ministry name (e.g., "Ministry of Road Transport & Highways")
                  - scheme: Scheme name (e.g., "Bharatmala Pariyojana")
                  - budget_category: Category (e.g., "Expenditure Budget")
                  - state: State/Central (e.g., "Central")
                  - document_type: Document type (e.g., "Demands for Grants")
        chunk_size: Target chunk size in tokens (default: 300)
        overlap: Overlap size in tokens (default: 75)
        
    Returns:
        List of chunk dictionaries with complete metadata:
        [
            {
                'text': str,
                'year': str,
                'ministry': str,
                'scheme': str,
                'budget_category': str,
                'state': str,
                'document_type': str,
                'page_number': int
            }
        ]
    """
    chunks = []
    chunker = _get_token_chunker()
    
    # Global chunk index for the entire document (to allow sequential retrieval)
    doc_chunk_index = 0
    
    for page_data in pages_data:
        page_text = page_data.get('text', '')
        page_number = page_data.get('page_number', 0)
        # Use document_name from metadata (includes .pdf extension) if available,
        # otherwise fall back to the one from page_data
        document_name = metadata.get('document_name') or page_data.get('document_name', 'unknown_doc')
        
        # Skip empty pages
        if not page_text.strip():
            continue
        
        # Split text into chunks with overlap (token-based)
        page_chunks = chunker.split_into_chunks(page_text, chunk_size, overlap)
        
        # Enrich each chunk with complete metadata
        for chunk_text in page_chunks:
            # Create a deterministic ID for this chunk
            chunk_id = f"{document_name}_chunk_{doc_chunk_index}"
            
            chunk = {
                'id': chunk_id,
                'text': chunk_text,
                'year': metadata.get('year', 'Unknown'),
                'ministry': metadata.get('ministry', 'Unknown'),
                'scheme': metadata.get('scheme', 'General'),
                'budget_category': metadata.get('budget_category', 'General'),
                'state': metadata.get('state', 'Central'),
                'document_type': metadata.get('document_type', 'Budget Document'),
                'page_number': page_number,
                'document_name': document_name,
                'chunk_index': doc_chunk_index
            }
            chunks.append(chunk)
            doc_chunk_index += 1
    
    return chunks


def _split_text_into_chunks(
    text: str, 
    chunk_size: int = 300, 
    overlap: int = 75
) -> List[str]:
    """
    Split text into overlapping chunks using token-based splitting.
    
    Args:
        text: Text to split
        chunk_size: Target size for each chunk in tokens (default: 300)
        overlap: Number of tokens to overlap between chunks (default: 75)
        
    Returns:
        List of text chunks
    """
    chunker = _get_token_chunker()
    return chunker.split_into_chunks(text, chunk_size, overlap)

