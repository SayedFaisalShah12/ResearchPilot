"""
ResearchPilot - Main Streamlit Application
Autonomous Research Assistant with Agentic RAG
"""

import streamlit as st
import time
from pathlib import Path

from memory.faiss_store import FAISSStore
from tools.vector_store import VectorStoreTool
from orchestrator.research_graph import ResearchGraph
import config

# Page configuration
st.set_page_config(
    page_title=config.STREAMLIT_TITLE,
    page_icon=config.STREAMLIT_PAGE_ICON,
    layout="wide"
)

# Initialize session state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "research_graph" not in st.session_state:
    st.session_state.research_graph = None
if "research_history" not in st.session_state:
    st.session_state.research_history = []


def initialize_system():
    """Initialize vector store and research graph"""
    if st.session_state.vector_store is None:
        with st.spinner("Initializing vector store..."):
            try:
                faiss_store = FAISSStore()
                vector_store_tool = VectorStoreTool(faiss_store)
                research_graph = ResearchGraph(vector_store_tool)
                
                st.session_state.vector_store = vector_store_tool
                st.session_state.research_graph = research_graph
                st.success("System initialized successfully!")
                return True
            except Exception as e:
                st.error(f"Initialization error: {e}")
                return False
    return True


def format_sources(sources: list) -> str:
    """Format sources list for display"""
    if not sources:
        return "No sources available"
    
    unique_sources = list(set(sources))
    formatted = []
    for i, source in enumerate(unique_sources, 1):
        if source.startswith("http"):
            formatted.append(f"{i}. [{source}]({source})")
        else:
            formatted.append(f"{i}. {source}")
    
    return "\n".join(formatted)


def main():
    """Main application"""
    st.title("🚀 ResearchPilot")
    st.markdown("**Autonomous Research Assistant:**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Initialize system
        if st.button("Initialize System", type="primary"):
            initialize_system()
        
        if st.session_state.vector_store:
            stats = st.session_state.vector_store.get_stats()
            st.success("✅ System Ready")
            st.info(f"📚 Knowledge Base: {stats['total_documents']} documents")
        else:
            st.warning("⚠️ System not initialized")
        
        st.divider()
        
        st.header("📖 Instructions")
        st.markdown("""
        1. Click "Initialize System" if not done
        2. Enter your research question
        3. Click "Start Research"
        4. Watch agents work autonomously
        5. Review the final answer with sources
        """)
        
        st.divider()
        
        st.header("📁 Document Management")
        st.markdown("Place PDF or text files in the `data/` folder to add them to the knowledge base.")
        
        if st.button("Check for Documents"):
            from tools.pdf_reader import PDFReader
            reader = PDFReader()
            docs = reader.list_documents()
            if docs:
                st.success(f"Found {len(docs)} document(s)")
                for doc in docs:
                    st.text(Path(doc).name)
            else:
                st.info("No documents found in data/ folder")
    
    # Main content area
    if not st.session_state.research_graph:
        st.info("👈 Please initialize the system from the sidebar first.")
        return
    
    # Research question input
    st.header("🔍 Research Question")
    question = st.text_input(
        "Enter your research question:",
        placeholder="e.g., What are the latest developments in quantum computing?",
        key="research_question"
    )
    
    # Start research button
    col1, col2 = st.columns([1, 4])
    with col1:
        start_research = st.button("🚀 Start Research", type="primary", disabled=not question)
    
    if start_research and question:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        agent_log = st.empty()
        
        # Create containers for results
        with st.container():
            st.header("🤖 Agent Activity")
            agent_container = st.empty()
        
        answer_container = st.container()
        sources_container = st.container()
        
        # Run research
        try:
            status_text.text("Starting research...")
            progress_bar.progress(10)
            
            # Track agent actions
            agent_actions = []
            
            # Run the research graph
            status_text.text("Executing research workflow...")
            progress_bar.progress(30)
            
            # Display agent activity
            with agent_container:
                st.markdown("**Agent Decisions:**")
                decision_placeholder = st.empty()
            
            # Run research (this will execute the full graph)
            final_state = st.session_state.research_graph.run(question)
            
            progress_bar.progress(80)
            status_text.text("Synthesizing final answer...")
            
            # Display agent history
            if final_state.get("history"):
                with agent_container:
                    st.markdown("**Agent Activity Log:**")
                    for action in final_state["history"]:
                        st.text(f"• {action}")
            
            progress_bar.progress(100)
            status_text.text("Research complete!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Display answer
            with answer_container:
                st.header("📝 Research Answer")
                answer = final_state.get("answer", "No answer generated.")
                st.markdown(answer)
            
            # Display sources
            with sources_container:
                st.header("📚 Sources")
                sources = final_state.get("sources", [])
                if sources:
                    st.markdown(format_sources(sources))
                else:
                    st.info("No sources available")
            
            # Save to history
            st.session_state.research_history.append({
                "question": question,
                "answer": answer,
                "sources": sources,
                "timestamp": time.time()
            })
            
        except Exception as e:
            st.error(f"Error during research: {str(e)}")
            st.exception(e)
    
    # Research history
    if st.session_state.research_history:
        st.divider()
        st.header("📜 Research History")
        
        for i, entry in enumerate(reversed(st.session_state.research_history[-5:]), 1):
            with st.expander(f"Research #{len(st.session_state.research_history) - i + 1}: {entry['question'][:50]}..."):
                st.markdown("**Question:** " + entry["question"])
                st.markdown("**Answer:** " + entry["answer"][:500] + "...")
                if entry["sources"]:
                    st.markdown("**Sources:** " + ", ".join(entry["sources"][:3]))


if __name__ == "__main__":
    main()

