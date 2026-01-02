"""
Reader Agent
Reads and processes documents (PDF/text)
"""

from typing import Dict, Any, List, Optional
from tools.pdf_reader import PDFReader
from tools.vector_store import VectorStoreTool
import config


class ReaderAgent:
    """
    Agent that reads documents and stores them in vector database
    """
    
    def __init__(self, vector_store_tool: VectorStoreTool):
        """
        Initialize reader agent
        
        Args:
            vector_store_tool: VectorStoreTool instance for storing documents
        """
        self.reader = PDFReader()
        self.vector_store = vector_store_tool
    
    def read_document(self, file_path: str) -> Dict[str, Any]:
        """
        Read a document and store in vector database
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with 'text', 'chunks', 'metadata', and 'stored'
        """
        # Determine file type and read
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.pdf'):
            doc_data = self.reader.read_pdf(file_path)
        elif file_path_lower.endswith('.txt'):
            doc_data = self.reader.read_text_file(file_path)
        else:
            return {
                "text": "",
                "chunks": [],
                "metadata": {"error": f"Unsupported file type: {file_path}"},
                "stored": False
            }
        
        # Store in vector database if we have chunks
        if doc_data.get("chunks") and not doc_data.get("metadata", {}).get("error"):
            try:
                source = doc_data.get("metadata", {}).get("filename", file_path)
                self.vector_store.add_documents(
                    doc_data["chunks"],
                    source=source,
                    file_path=file_path,
                    **doc_data.get("metadata", {})
                )
                doc_data["stored"] = True
            except Exception as e:
                print(f"Error storing document: {e}")
                doc_data["stored"] = False
        else:
            doc_data["stored"] = False
        
        return doc_data
    
    def list_available_documents(self, directory: str = None) -> List[str]:
        """
        List available documents
        
        Args:
            directory: Directory to search (defaults to data/)
            
        Returns:
            List of file paths
        """
        return self.reader.list_documents(directory)
    
    def read_multiple_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Read multiple documents
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of document data dictionaries
        """
        results = []
        for file_path in file_paths:
            result = self.read_document(file_path)
            results.append(result)
        return results

