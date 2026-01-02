"""
FAISS Vector Store Implementation
Handles document storage, embedding, and retrieval
"""

import pickle
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class FAISSStore:
    """
    Persistent FAISS vector store for document embeddings
    Uses sentence-transformers for embeddings
    """
    
    def __init__(self, embedding_model_name: str = config.EMBEDDING_MODEL):
        """
        Initialize FAISS store with embedding model
        
        Args:
            embedding_model_name: Name of the sentence-transformers model
        """
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.dimension = config.EMBEDDING_DIMENSION
        self.index = None
        self.metadata = []  # Store document metadata
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(config.VECTOR_STORE_FILE) and os.path.exists(config.METADATA_FILE):
            try:
                # Load existing index
                self.index = faiss.read_index(str(config.VECTOR_STORE_FILE))
                with open(config.METADATA_FILE, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded existing vector store with {self.index.ntotal} documents")
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Use L2 distance (Euclidean) - works well with normalized embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("Created new vector store")
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """
        Add documents to the vector store
        
        Args:
            texts: List of text documents to add
            metadatas: Optional list of metadata dictionaries for each document
        """
        if not texts:
            return
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True  # Normalize for better cosine similarity
        )
        
        # Convert to numpy array
        embeddings = np.array(embeddings).astype('float32')
        
        # Prepare metadata
        if metadatas is None:
            metadatas = [{"source": "unknown", "text": text} for text in texts]
        else:
            # Ensure text is in metadata
            for i, (text, meta) in enumerate(zip(texts, metadatas)):
                if "text" not in meta:
                    meta["text"] = text
        
        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        
        print(f"Added {len(texts)} documents. Total: {self.index.ntotal}")
    
    def search(self, query: str, k: int = config.TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'score'
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True
        )
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = {
                    "text": self.metadata[idx].get("text", ""),
                    "metadata": self.metadata[idx],
                    "score": float(distance),  # L2 distance (lower is better)
                    "rank": i + 1
                }
                results.append(result)
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        if self.index is not None:
            faiss.write_index(self.index, str(config.VECTOR_STORE_FILE))
            with open(config.METADATA_FILE, 'wb') as f:
                pickle.dump(self.metadata, f)
            print(f"Saved vector store with {self.index.ntotal} documents")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "total_documents": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "embedding_model": config.EMBEDDING_MODEL
        }

