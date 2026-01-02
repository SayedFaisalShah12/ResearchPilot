"""
Setup Verification Script
Checks if all dependencies and components are properly configured
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required. Current:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_ollama():
    """Check if Ollama is accessible"""
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        model_names = [m['name'] for m in models.get('models', [])]
        
        if 'llama3' in model_names:
            print("✅ Ollama is running and llama3 model is available")
            return True
        else:
            print("⚠️  Ollama is running but llama3 model not found")
            print(f"   Available models: {', '.join(model_names)}")
            print("   Run: ollama pull llama3")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("   Make sure Ollama is installed and running")
        return False

def check_imports():
    """Check if all required packages can be imported"""
    packages = [
        "langchain",
        "langchain_community",
        "langgraph",
        "faiss",
        "sentence_transformers",
        "duckduckgo_search",
        "fitz",  # PyMuPDF
        "pdfplumber",
        "streamlit"
    ]
    
    failed = []
    for package in packages:
        try:
            if package == "fitz":
                import fitz
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            failed.append(package)
    
    return len(failed) == 0

def check_project_structure():
    """Check if project structure is correct"""
    required_dirs = [
        "agents",
        "tools",
        "memory",
        "orchestrator",
        "data"
    ]
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Directory: {dir_name}/")
        else:
            print(f"❌ Missing directory: {dir_name}/")
            all_good = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ File: {file_name}")
        else:
            print(f"❌ Missing file: {file_name}")
            all_good = False
    
    return all_good

def main():
    """Run all checks"""
    print("=" * 50)
    print("ResearchPilot Setup Verification")
    print("=" * 50)
    print()
    
    print("1. Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("2. Checking Ollama...")
    ollama_ok = check_ollama()
    print()
    
    print("3. Checking package imports...")
    imports_ok = check_imports()
    print()
    
    print("4. Checking project structure...")
    structure_ok = check_project_structure()
    print()
    
    print("=" * 50)
    if python_ok and ollama_ok and imports_ok and structure_ok:
        print("✅ All checks passed! System is ready.")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

