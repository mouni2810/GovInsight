"""
Utility Module for GovInsight

This module provides helper functions for vector store management,
embeddings, and other utilities.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Union
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VectorStoreManager:
    """
    Manages ChromaDB vector store for budget document embeddings.
    """
    
    def __init__(
        self,
        persist_directory: str = "vectorstore",
        collection_name: str = "govinsight_budget_docs"
    ):
        """
        Initialize vector store manager with persistent storage.
        
        Args:
            persist_directory: Directory for persistent vector store storage
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = self._initialize_client()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _initialize_client(self) -> chromadb.Client:
        """
        Initialize ChromaDB client with persistent storage settings.
        
        Returns:
            ChromaDB client instance
        """
        # Use PersistentClient for proper disk persistence
        client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        print(f"ChromaDB client initialized with persistent storage: {self.persist_directory}")
        
        return client
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """
        Get existing collection or create new one with cosine similarity.
        
        Also verifies embedding model consistency to prevent retrieval issues.
        
        Returns:
            ChromaDB collection instance
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.collection_name
            )
            print(f"Loaded existing collection: {self.collection_name}")
            print(f"Collection contains {collection.count()} documents")
            
            # CRITICAL: Verify embedding model consistency
            stored_model = collection.metadata.get("embedding_model", "unknown")
            current_model = os.getenv("EMBEDDING_MODEL", "huggingface")
            
            if stored_model != "unknown" and stored_model != current_model:
                print(f"\n⚠️  WARNING: EMBEDDING MODEL MISMATCH DETECTED!")
                print(f"   Collection was indexed with: {stored_model}")
                print(f"   Currently configured to use: {current_model}")
                print(f"   This WILL cause poor retrieval quality!")
                print(f"   Solution: Re-index with: python app/rag_pipeline.py --index --reset\n")
            elif stored_model == current_model:
                print(f"✓ Embedding model verified: {current_model}")
            
        except Exception:
            # Create new collection if it doesn't exist
            current_model = os.getenv("EMBEDDING_MODEL", "huggingface")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",  # Use cosine similarity
                    "embedding_model": current_model,  # Track embedding model
                    "description": "Indian Government Budget Documents"
                }
            )
            print(f"Created new collection: {self.collection_name}")
            print(f"Embedding model: {current_model}")
        
        return collection
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents with embeddings and metadata to the vector store.
        
        Args:
            documents: List of document text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries for each document
            ids: Optional list of unique IDs (auto-generated if not provided)
        """
        # Generate IDs if not provided
        if ids is None:
            start_idx = self.collection.count()
            ids = [f"doc_{start_idx + i}" for i in range(len(documents))]
        
        # Validate inputs
        if not (len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("Documents, embeddings, and metadatas must have the same length")
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} documents to collection")
        print(f"Total documents in collection: {self.collection.count()}")
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the current collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        
        stats = {
            "collection_name": self.collection_name,
            "total_documents": count,
            "persist_directory": str(self.persist_directory),
            "metadata": self.collection.metadata
        }
        
        return stats
    
    def reset_collection(self) -> None:
        """
        Delete and recreate the collection (WARNING: deletes all data).
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Collection deletion skipped: {e}")
        
        # Recreate collection
        self.collection = self._get_or_create_collection()
        print("Collection reset complete")
    
    def delete_collection(self) -> None:
        """
        Permanently delete the collection and all its data.
        """
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def persist(self) -> None:
        """
        Explicitly persist data to disk (automatic in newer ChromaDB versions).
        """
        # Modern ChromaDB auto-persists, but keeping for compatibility
        print("Data persisted to disk")


def initialize_vector_store(
    persist_directory: str = "vectorstore",
    collection_name: str = "govinsight_budget_docs",
    reset: bool = False
) -> VectorStoreManager:
    """
    Initialize or load the vector store.
    
    Args:
        persist_directory: Directory for persistent storage
        collection_name: Name of the collection
        reset: If True, delete existing collection and start fresh
        
    Returns:
        VectorStoreManager instance
    """
    manager = VectorStoreManager(
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    if reset:
        print("Resetting vector store...")
        manager.reset_collection()
    
    return manager


def format_metadata_for_storage(chunk: Dict) -> Dict:
    """
    Format chunk metadata for ChromaDB storage.
    
    ChromaDB has restrictions on metadata types (only str, int, float, bool).
    This function ensures all metadata is properly formatted AND complete,
    guaranteeing that every chunk has all required metadata fields.
    
    This prevents KeyError exceptions during queries by ensuring
    fields like 'year', 'ministry', 'scheme' are always present.
    
    Args:
        chunk: Chunk dictionary with text and metadata
        
    Returns:
        Formatted metadata dictionary safe for ChromaDB with all required fields
    """
    # Define required fields with their default values
    # This ensures every chunk has complete metadata schema
    metadata = {
        "year": str(chunk.get("year", "Unknown") or "Unknown"),
        "ministry": str(chunk.get("ministry", "Unknown") or "Unknown"),
        "scheme": str(chunk.get("scheme", "General") or "General"),
        "budget_category": str(chunk.get("budget_category", "General") or "General"),
        "state": str(chunk.get("state", "Central") or "Central"),
        "document_type": str(chunk.get("document_type", "Budget Document") or "Budget Document"),
        "page_number": int(chunk.get("page_number", 0) or 0),
        # Context fields for retrieval
        "document_name": str(chunk.get("document_name", "")),
        "chunk_index": int(chunk.get("chunk_index", -1)),
        "id": str(chunk.get("id", "")),
        # Content density fields for reranking
        "token_count": int(chunk.get("token_count", 0) or 0),
        "char_length": int(chunk.get("char_length", 0) or 0),
        "has_numbers": bool(chunk.get("has_numbers", False)),
        "number_density": float(chunk.get("number_density", 0.0) or 0.0)
    }
    
    # Ensure no empty strings (replace with defaults)
    if not metadata["year"].strip():
        metadata["year"] = "Unknown"
    if not metadata["ministry"].strip():
        metadata["ministry"] = "Unknown"
    if not metadata["scheme"].strip():
        metadata["scheme"] = "General"
    if not metadata["budget_category"].strip():
        metadata["budget_category"] = "General"
    if not metadata["state"].strip():
        metadata["state"] = "Central"
    if not metadata["document_type"].strip():
        metadata["document_type"] = "Budget Document"
    
    return metadata


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using Gemini or HuggingFace models.
    """
    
    def __init__(self, model_type: str = "gemini", model_name: Optional[str] = None):
        """
        Initialize embedding generator.
        
        Args:
            model_type: Type of embedding model ("gemini" or "huggingface")
            model_name: Optional specific model name (uses default if not provided)
        """
        self.model_type = model_type.lower()
        self.model_name = model_name
        self.embed_model = None
        
        # Initialize the appropriate model
        if self.model_type == "gemini":
            self._initialize_gemini_embeddings()
        elif self.model_type == "huggingface":
            self._initialize_huggingface_embeddings()
        else:
            raise ValueError(f"Unsupported model type: {model_type}. Use 'gemini' or 'huggingface'")
    
    def _initialize_gemini_embeddings(self) -> None:
        """
        Initialize Gemini embeddings model.
        """
        try:
            import google.generativeai as genai
            from llama_index.embeddings.gemini import GeminiEmbedding
            
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Initialize embedding model
            model = self.model_name or "models/embedding-001"
            self.embed_model = GeminiEmbedding(model_name=model, api_key=api_key)
            
            print(f"Initialized Gemini embeddings: {model}")
            
        except ImportError as e:
            print(f"Error importing Gemini dependencies: {e}")
            print("Install with: pip install llama-index-embeddings-gemini google-generativeai")
            raise
    
    def _initialize_huggingface_embeddings(self) -> None:
        """
        Initialize HuggingFace embeddings model as fallback.
        """
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            
            # Use default sentence-transformers model
            model = self.model_name or "sentence-transformers/all-MiniLM-L6-v2"
            self.embed_model = HuggingFaceEmbedding(model_name=model)
            
            print(f"Initialized HuggingFace embeddings: {model}")
            
        except ImportError as e:
            print(f"Error importing HuggingFace dependencies: {e}")
            print("Install with: pip install llama-index-embeddings-huggingface sentence-transformers")
            raise
    
    def get_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not self.embed_model:
            raise RuntimeError("Embedding model not initialized")
        
        # LlamaIndex embedding models have get_text_embedding method
        embedding = self.embed_model.get_text_embedding(text)
        
        return embedding
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.embed_model:
            raise RuntimeError("Embedding model not initialized")
        
        # Use batch method if available, otherwise fallback to individual
        try:
            embeddings = self.embed_model.get_text_embedding_batch(texts)
        except AttributeError:
            # Fallback to individual embeddings
            embeddings = [self.get_text_embedding(text) for text in texts]
        
        return embeddings
    
    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query string (same as text embedding for these models).
        
        Args:
            query: Query text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # For most models, query and text embeddings are the same
        # Some models have separate query_embedding methods
        try:
            embedding = self.embed_model.get_query_embedding(query)
        except AttributeError:
            embedding = self.get_text_embedding(query)
        
        return embedding


def initialize_embeddings(
    model_type: str = "gemini",
    model_name: Optional[str] = None
) -> EmbeddingGenerator:
    """
    Initialize embedding generator with specified model.
    
    Args:
        model_type: Type of model ("gemini" or "huggingface")
        model_name: Optional specific model name
        
    Returns:
        Initialized EmbeddingGenerator instance
    """
    try:
        generator = EmbeddingGenerator(model_type=model_type, model_name=model_name)
        return generator
    except Exception as e:
        print(f"Failed to initialize {model_type} embeddings: {e}")
        if model_type == "gemini":
            print("Falling back to HuggingFace embeddings...")
            return EmbeddingGenerator(model_type="huggingface")
        else:
            raise


def embed_chunks(chunks: List[Dict], embedding_generator: EmbeddingGenerator) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks with batch processing.
    
    Args:
        chunks: List of chunk dictionaries containing 'text' field
        embedding_generator: Initialized EmbeddingGenerator instance
        
    Returns:
        List of embedding vectors
    """
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Use batch processing for better performance
    batch_size = 500
    all_embeddings = []
    
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    for i in range(0, len(texts), batch_size):
        batch_num = (i // batch_size) + 1
        batch_texts = texts[i:i + batch_size]
        
        print(f"  Processing batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)...")
        
        # Generate embeddings for this batch
        batch_embeddings = embedding_generator.get_text_embedding_batch(batch_texts)
        all_embeddings.extend(batch_embeddings)
    
    print(f"Generated {len(all_embeddings)} embeddings")
    
    return all_embeddings

