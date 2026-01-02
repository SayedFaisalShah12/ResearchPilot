"""
Configuration file for ResearchPilot
Contains all system settings and constants
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_STORE_PATH = DATA_DIR / "faiss_index"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
VECTOR_STORE_PATH.mkdir(exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Embedding Model
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384  # Dimension for bge-small-en-v1.5

# Vector Store Configuration
FAISS_INDEX_NAME = "research_index"
VECTOR_STORE_FILE = VECTOR_STORE_PATH / f"{FAISS_INDEX_NAME}.faiss"
METADATA_FILE = VECTOR_STORE_PATH / f"{FAISS_INDEX_NAME}.pkl"

# RAG Configuration
TOP_K_RESULTS = 5  # Number of chunks to retrieve
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Agent Configuration
MAX_SEARCH_RESULTS = 5  # Maximum web search results
MAX_ITERATIONS = 10  # Maximum agent iterations
TEMPERATURE = 0.7  # LLM temperature

# Streamlit Configuration
STREAMLIT_TITLE = "ResearchPilot - Autonomous Research Assistant"
STREAMLIT_PAGE_ICON = "🚀"

# Action Types
class ActionType:
    SEARCH = "SEARCH"
    READ = "READ"
    RETRIEVE = "RETRIEVE"
    ANSWER = "ANSWER"
    DONE = "DONE"

