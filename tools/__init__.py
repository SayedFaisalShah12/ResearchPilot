"""
Tools module for ResearchPilot
Contains utility tools for search, document reading, etc.
"""

try:
    # Try relative imports (when used as a package)
    from .search_tool import DuckDuckGoSearchTool
    from .pdf_reader import PDFReader
    from .vector_store import VectorStoreTool
except ImportError:
    # Fall back to absolute imports (when run directly)
    import sys
    from pathlib import Path
    
    # Get the directory containing this file
    try:
        parent_dir = str(Path(__file__).parent.parent)
    except NameError:
        # If __file__ is not defined, use current working directory
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath('.')))
    
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from tools.search_tool import DuckDuckGoSearchTool
    from tools.pdf_reader import PDFReader
    from tools.vector_store import VectorStoreTool

__all__ = ["DuckDuckGoSearchTool", "PDFReader", "VectorStoreTool"]

