"""
Search Agent
Performs web searches and processes results
"""

from typing import Dict, Any, List
from tools.search_tool import DuckDuckGoSearchTool
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class SearchAgent:
    """
    Agent that performs web searches and extracts relevant information
    """
    
    def __init__(self):
        """Initialize search agent"""
        self.search_tool = DuckDuckGoSearchTool()
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=config.TEMPERATURE
        )
        
        self.summarize_prompt = PromptTemplate(
            input_variables=["question", "search_results"],
            template="""You are a search agent. You have performed a web search and received results.

Research Question: {question}

Search Results:
{search_results}

Your task:
1. Extract the most relevant information from the search results
2. Summarize key findings
3. Note the sources

Provide a concise summary of the relevant information found, including source URLs.
"""
        )
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Perform web search and process results
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with 'results', 'summary', and 'sources'
        """
        # Perform search
        raw_results = self.search_tool.search(query)
        
        if not raw_results:
            return {
                "results": [],
                "summary": "No search results found.",
                "sources": []
            }
        
        # Format results for LLM
        formatted_results = self.search_tool.format_results(raw_results)
        
        # Summarize with LLM
        try:
            prompt = self.summarize_prompt.format(
                question=query,
                search_results=formatted_results
            )
            summary = self.llm.invoke(prompt)
        except Exception as e:
            print(f"Search agent summarization error: {e}")
            summary = formatted_results
        
        # Extract sources
        sources = [r.get("url", "") for r in raw_results if r.get("url")]
        
        return {
            "results": raw_results,
            "summary": summary,
            "sources": sources,
            "raw_text": formatted_results
        }

