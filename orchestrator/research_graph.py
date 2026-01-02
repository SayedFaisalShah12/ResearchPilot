"""
Research Graph - LangGraph Orchestrator
Coordinates all agents in the research workflow
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

from agents.planner import PlannerAgent
from agents.search_agent import SearchAgent
from agents.reader_agent import ReaderAgent
from agents.retriever_agent import RetrieverAgent
from agents.reasoning_agent import ReasoningAgent
from tools.vector_store import VectorStoreTool
import config


class ResearchState(TypedDict):
    """State structure for the research graph"""
    question: str
    current_action: str
    context: str
    search_info: str
    retrieved_info: str
    document_info: str
    answer: str
    sources: List[str]
    history: Annotated[List[str], operator.add]
    iteration: int


class ResearchGraph:
    """
    LangGraph-based orchestrator for research workflow
    Coordinates planner, search, reader, retriever, and reasoning agents
    """
    
    def __init__(self, vector_store_tool: VectorStoreTool):
        """
        Initialize research graph
        
        Args:
            vector_store_tool: VectorStoreTool instance
        """
        # Initialize agents
        self.planner = PlannerAgent()
        self.search_agent = SearchAgent()
        self.reader_agent = ReaderAgent(vector_store_tool)
        self.retriever_agent = RetrieverAgent(vector_store_tool)
        self.reasoning_agent = ReasoningAgent()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planner", self._plan_node)
        workflow.add_node("search", self._search_node)
        workflow.add_node("read", self._read_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("answer", self._answer_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add conditional edges from planner
        workflow.add_conditional_edges(
            "planner",
            self._route_after_planning,
            {
                config.ActionType.SEARCH: "search",
                config.ActionType.READ: "read",
                config.ActionType.RETRIEVE: "retrieve",
                config.ActionType.ANSWER: "answer",
                config.ActionType.DONE: END
            }
        )
        
        # Add edges from action nodes back to planner
        workflow.add_edge("search", "planner")
        workflow.add_edge("read", "planner")
        workflow.add_edge("retrieve", "planner")
        
        # Answer node ends
        workflow.add_edge("answer", END)
        
        return workflow.compile()
    
    def _plan_node(self, state: ResearchState) -> ResearchState:
        """Planning node - decides next action"""
        question = state.get("question", "")
        context = state.get("context", "")
        history = state.get("history", [])
        iteration = state.get("iteration", 0) + 1
        
        # Check max iterations
        if iteration > config.MAX_ITERATIONS:
            return {
                **state,
                "current_action": config.ActionType.ANSWER,
                "iteration": iteration
            }
        
        # Get next action from planner
        action = self.planner.plan(question, context, history)
        
        return {
            **state,
            "current_action": action,
            "iteration": iteration,
            "history": [f"Iteration {iteration}: Planned action: {action}"]
        }
    
    def _search_node(self, state: ResearchState) -> ResearchState:
        """Search node - performs web search"""
        question = state.get("question", "")
        
        # Perform search
        search_result = self.search_agent.search(question)
        
        # Update state
        search_info = search_result.get("summary", "")
        sources = state.get("sources", [])
        sources.extend(search_result.get("sources", []))
        
        # Update context
        context = state.get("context", "")
        context += f"\n\nWeb Search Results:\n{search_info}"
        
        return {
            **state,
            "search_info": search_info,
            "context": context,
            "sources": sources,
            "history": [f"Performed web search for: {question}"]
        }
    
    def _read_node(self, state: ResearchState) -> ResearchState:
        """Read node - reads documents"""
        # List available documents
        available_docs = self.reader_agent.list_available_documents()
        
        if not available_docs:
            return {
                **state,
                "document_info": "No documents available to read.",
                "history": ["No documents found to read"]
            }
        
        # Read all available documents
        doc_results = self.reader_agent.read_multiple_documents(available_docs)
        
        # Summarize document info
        doc_info_parts = []
        sources = state.get("sources", [])
        
        for doc_result in doc_results:
            if doc_result.get("stored"):
                filename = doc_result.get("metadata", {}).get("filename", "unknown")
                doc_info_parts.append(f"Read and stored document: {filename}")
                sources.append(filename)
        
        document_info = "\n".join(doc_info_parts) if doc_info_parts else "No documents were successfully read."
        
        # Update context
        context = state.get("context", "")
        context += f"\n\nDocuments Read:\n{document_info}"
        
        return {
            **state,
            "document_info": document_info,
            "context": context,
            "sources": sources,
            "history": [f"Read {len(doc_results)} document(s)"]
        }
    
    def _retrieve_node(self, state: ResearchState) -> ResearchState:
        """Retrieve node - retrieves from vector store"""
        question = state.get("question", "")
        
        # Retrieve from vector store
        retrieve_result = self.retriever_agent.retrieve(question)
        
        # Update state
        retrieved_info = retrieve_result.get("summary", "")
        sources = state.get("sources", [])
        sources.extend(retrieve_result.get("sources", []))
        
        # Update context
        context = state.get("context", "")
        context += f"\n\nKnowledge Base Retrieval:\n{retrieved_info}"
        
        return {
            **state,
            "retrieved_info": retrieved_info,
            "context": context,
            "sources": sources,
            "history": [f"Retrieved information from knowledge base"]
        }
    
    def _answer_node(self, state: ResearchState) -> ResearchState:
        """Answer node - synthesizes final answer"""
        question = state.get("question", "")
        search_info = state.get("search_info", "")
        retrieved_info = state.get("retrieved_info", "")
        document_info = state.get("document_info", "")
        
        # Synthesize answer
        answer_result = self.reasoning_agent.synthesize_answer(
            question,
            search_info,
            retrieved_info,
            document_info
        )
        
        return {
            **state,
            "answer": answer_result.get("answer", ""),
            "current_action": config.ActionType.DONE
        }
    
    def _route_after_planning(self, state: ResearchState) -> str:
        """Route to next node based on planned action"""
        return state.get("current_action", config.ActionType.SEARCH)
    
    def run(self, question: str) -> Dict[str, Any]:
        """
        Run the research workflow
        
        Args:
            question: Research question
            
        Returns:
            Final state dictionary with answer and sources
        """
        # Initial state
        initial_state: ResearchState = {
            "question": question,
            "current_action": "",
            "context": "",
            "search_info": "",
            "retrieved_info": "",
            "document_info": "",
            "answer": "",
            "sources": [],
            "history": [],
            "iteration": 0
        }
        
        # Run graph
        try:
            final_state = self.graph.invoke(initial_state)
            return final_state
        except Exception as e:
            print(f"Graph execution error: {e}")
            return {
                **initial_state,
                "answer": f"Error during research: {str(e)}",
                "current_action": config.ActionType.DONE
            }

