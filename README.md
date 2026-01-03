# ResearchPilot
ResearchPilot is an end-to-end autonomous research assistant built using free and open-source tools. It combines local LLMs (via Ollama), LangGraph-style agent orchestration, and FAISS vector search to enable private, extensible research workflows without paid APIs.

**Key Features**
- **Local-first:** Works with locally-hosted LLMs (Ollama) and an on-disk FAISS index.
- **Agent-based:** Multiple agents coordinate to retrieve, read, reason, and search research material.
- **Pluggable tools:** Tools for PDF reading, vector storage, and searching are included and easy to extend.

**Repository layout**
- **config:** [config.py](config.py) — project configuration and runtime options.
- **entrypoint:** [main.py](main.py) — simple launcher for running the system.
- **agents:** contains agent implementations: [agents/planner.py](agents/planner.py), [agents/retriever_agent.py](agents/retriever_agent.py), [agents/search_agent.py](agents/search_agent.py), [agents/reader_agent.py](agents/reader_agent.py), [agents/reasoning_agent.py](agents/reasoning_agent.py).
- **tools:** utilities for reading PDFs and vector storage: [tools/pdf_reader.py](tools/pdf_reader.py), [tools/vector_store.py](tools/vector_store.py), [tools/search_tool.py](tools/search_tool.py).
- **data:** FAISS index: [data/faiss_index/research_index.faiss](data/faiss_index/research_index.faiss).
- **memory:** FAISS-backed memory helper: [memory/faiss_store.py](memory/faiss_store.py).
- **orchestrator:** research graph/orchestration helpers: [orchestrator/research_graph.py](orchestrator/research_graph.py).

**Prerequisites**
- Python 3.10+
- System requirements for FAISS (prebuilt wheels available on many platforms)
- Optional: Ollama or another local LLM runtime if you want fully local LLMs

**Install**
1. Create a virtual environment and activate it.

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows: .venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

**Quick setup / verification**
- Run the provided setup verifier:

```bash
python verify_setup.py
```

- If using a local LLM (Ollama), ensure the runtime is running and reachable per your `config.py` settings.

**Usage**
- Basic run (starts the main entrypoint):

```bash
python main.py
```

- Run a specific agent module for development or debugging, for example:

```bash
python -m agents.search_agent
```

- Inspect or rebuild the FAISS index using the tools in `tools/` and `memory/faiss_store.py`.

**Configuration**
- Edit [config.py](config.py) to change runtime options (LLM endpoint, index paths, logging).
- The default FAISS index path is `data/faiss_index/research_index.faiss` — update it if you store indexes elsewhere.

**Architecture (high-level)**
- **Agents:** Independent components that perform focused tasks (search, retrieval, reading, reasoning, planning).
- **Tools:** Small, testable utilities used by agents to access external resources (PDFs, vector DBs).
- **Orchestrator:** Coordinates agent workflows and builds a research graph to track context and progress.

**Development & Testing**
- Run unit-style checks by executing individual modules. Use `inspect_*.py` scripts in `scripts/` to introspect protobufs or runtime artifacts.

**Contributing**
- Feel free to open issues or pull requests. Keep changes focused and add tests for new functionality.

**License**
- This project is provided as-is. Add a LICENSE file if you want an explicit license.

---

If you'd like, I can also:
- add usage examples for common workflows,
- add a minimal LICENSE file,
- or create example scripts to rebuild the FAISS index from PDFs.
