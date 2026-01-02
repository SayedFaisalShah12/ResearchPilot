"""
DuckDuckGo Search Tool
Provides web search functionality using DuckDuckGo
"""

from typing import List, Dict, Any
from duckduckgo_search import DDGS
import config


class DuckDuckGoSearchTool:
    """
    Tool for performing web searches using DuckDuckGo
    Free and doesn't require API keys
    """
    
    def __init__(self, max_results: int = config.MAX_SEARCH_RESULTS):
        """
        Initialize search tool
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, snippet, and URL
        """
        try:
            results = []
            with DDGS() as ddgs:
                # Perform text search
                search_results = ddgs.text(
                    query,
                    max_results=self.max_results
                )
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", ""),
                        "source": "web_search"
                    })
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return [{
                "title": "Search Error",
                "snippet": f"Unable to perform search: {str(e)}",
                "url": "",
                "source": "error"
            }]
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results as readable text
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string of search results
        """
        if not results:
            return "No search results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"[{i}] {result['title']}\n"
                f"    {result['snippet']}\n"
                f"    Source: {result['url']}\n"
            )
        
        return "\n".join(formatted)

