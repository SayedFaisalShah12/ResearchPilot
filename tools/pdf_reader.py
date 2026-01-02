"""
PDF Reader Tool
Extracts text from PDF documents using PyMuPDF and pdfplumber
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import pdfplumber
import config


class PDFReader:
    """
    Tool for reading and extracting text from PDF documents
    Uses PyMuPDF as primary, pdfplumber as fallback
    """
    
    def __init__(self):
        """Initialize PDF reader"""
        pass
    
    def read_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Read PDF file and extract text
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with 'text', 'pages', and 'metadata'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "text": "",
                "pages": 0,
                "metadata": {"error": f"File not found: {file_path}"},
                "chunks": []
            }
        
        # Try PyMuPDF first (faster)
        try:
            return self._read_with_pymupdf(file_path)
        except Exception as e:
            print(f"PyMuPDF failed: {e}. Trying pdfplumber...")
            try:
                return self._read_with_pdfplumber(file_path)
            except Exception as e2:
                return {
                    "text": "",
                    "pages": 0,
                    "metadata": {"error": f"Both PDF readers failed: {str(e2)}"},
                    "chunks": []
                }
    
    def _read_with_pymupdf(self, file_path: Path) -> Dict[str, Any]:
        """Read PDF using PyMuPDF"""
        doc = fitz.open(file_path)
        pages = []
        full_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages.append({
                "page": page_num + 1,
                "text": text
            })
            full_text.append(text)
        
        full_text_str = "\n\n".join(full_text)
        chunks = self._chunk_text(full_text_str)
        
        metadata = {
            "filename": file_path.name,
            "total_pages": len(doc),
            "method": "pymupdf"
        }
        
        doc.close()
        
        return {
            "text": full_text_str,
            "pages": pages,
            "metadata": metadata,
            "chunks": chunks
        }
    
    def _read_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Read PDF using pdfplumber (fallback)"""
        pages = []
        full_text = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append({
                    "page": page_num + 1,
                    "text": text
                })
                full_text.append(text)
        
        full_text_str = "\n\n".join(full_text)
        chunks = self._chunk_text(full_text_str)
        
        metadata = {
            "filename": file_path.name,
            "total_pages": len(pages),
            "method": "pdfplumber"
        }
        
        return {
            "text": full_text_str,
            "pages": pages,
            "metadata": metadata,
            "chunks": chunks
        }
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for vector storage
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        chunk_size = config.CHUNK_SIZE
        overlap = config.CHUNK_OVERLAP
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only if reasonable
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap  # Overlap for context
        
        return chunks
    
    def read_text_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read plain text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with 'text' and 'chunks'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "text": "",
                "chunks": [],
                "metadata": {"error": f"File not found: {file_path}"}
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self._chunk_text(text)
            
            return {
                "text": text,
                "chunks": chunks,
                "metadata": {
                    "filename": file_path.name,
                    "method": "text_file"
                }
            }
        except Exception as e:
            return {
                "text": "",
                "chunks": [],
                "metadata": {"error": str(e)}
            }
    
    def list_documents(self, directory: str = None) -> List[str]:
        """
        List available PDF and text files in data directory
        
        Args:
            directory: Directory to search (defaults to data/)
            
        Returns:
            List of file paths
        """
        if directory is None:
            directory = config.DATA_DIR
        else:
            directory = Path(directory)
        
        files = []
        
        # Find PDFs
        for pdf_file in directory.glob("*.pdf"):
            files.append(str(pdf_file))
        
        # Find text files
        for txt_file in directory.glob("*.txt"):
            files.append(str(txt_file))
        
        return files

