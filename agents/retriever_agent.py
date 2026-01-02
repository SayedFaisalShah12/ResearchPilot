"""
Retriever Agent
Retrieves relevant information from vector store
"""

from typing import Dict, Any, List
from tools.vector_store import VectorStoreTool
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class RetrieverAgent:
    """
    Agent that retrieves relevant information from the knowledge base
    """
    
    def __init__(self, vector_store_tool: VectorStoreTool):
        """
        Initialize retriever agent
        
        Args:
            vector_store_tool: VectorStoreTool instance
        """
        self.vector_store = vector_store_tool
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=config.TEMPERATURE
        )
        
        self.summarize_prompt = PromptTemplate(
            input_variables=["question", "retrieved_docs"],
            template="""You are a retrieval agent. You have retrieved relevant documents from the knowledge base.

Research Question: {question}

Retrieved Documents:
{retrieved_docs}

Your task:
1. Extract the most relevant information from the retrieved documents
2. Summarize how this information relates to the question
3. Note the sources

Provide a concise summary of the relevant information retrieved.
"""
        )
    
    def retrieve(self, query: str, k: int = config.TOP_K_RESULTS) -> Dict[str, Any]:
        """
        Retrieve relevant documents from vector store
        
        Args:
            query: Search query
            k: Number of results to retrieve
            
        Returns:
            Dictionary with 'results', 'summary', and 'sources'
        """
        # Retrieve from vector store
        results = self.vector_store.search(query, k)
        
        if not results:
            return {
                "results": [],
                "summary": "No relevant documents found in knowledge base.",
                "sources": []
            }
        
        # Format results
        formatted_results = self.vector_store.format_results(results)
        
        # Summarize with LLM
        try:
            prompt = self.summarize_prompt.format(
                question=query,
                retrieved_docs=formatted_results
            )
            summary = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Retriever agent summarization error: {e}")
            summary = formatted_results
        
        # Extract sources
        sources = []
        for result in results:
            source = result.get("metadata", {}).get("source", "unknown")
            if source not in sources:
                sources.append(source)
        
        return {
            "results": results,
            "summary": summary,
            "sources": sources,
            "raw_text": formatted_results
        }

