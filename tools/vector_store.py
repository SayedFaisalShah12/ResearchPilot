"""
Vector Store Tool
Wrapper for FAISS store operations
"""

from typing import List, Dict, Any
from memory.faiss_store import FAISSStore
import config


class VectorStoreTool:
    """
    Tool for interacting with the vector store
    Provides high-level interface for agents
    """
    
    def __init__(self, faiss_store: FAISSStore):
        """
        Initialize vector store tool
        
        Args:
            faiss_store: FAISSStore instance
        """
        self.store = faiss_store
    
    def add_documents(self, texts: List[str], source: str = "unknown", **metadata):
        """
        Add documents to vector store
        
        Args:
            texts: List of text documents
            source: Source identifier
            **metadata: Additional metadata
        """
        metadatas = [
            {
                "source": source,
                "text": text,
                **metadata
            }
            for text in texts
        ]
        self.store.add_documents(texts, metadatas)
        self.store.save()
    
    def search(self, query: str, k: int = config.TOP_K_RESULTS) -> List[Dict[str, Any]]:
        """
        Search vector store
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of search results
        """
        return self.store.search(query, k)
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results as readable text
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string
        """
        if not results:
            return "No relevant documents found in knowledge base."
        
        formatted = []
        for result in results:
            source = result.get("metadata", {}).get("source", "unknown")
            text = result.get("text", "")[:500]  # Limit length
            score = result.get("score", 0)
            
            formatted.append(
                f"Source: {source}\n"
                f"Relevance Score: {score:.4f}\n"
                f"Content: {text}...\n"
            )
        
        return "\n\n".join(formatted)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.store.get_stats()

