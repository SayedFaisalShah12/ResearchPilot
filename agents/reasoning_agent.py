"""
Reasoning Agent
Synthesizes final answer from all gathered information
"""

from typing import Dict, Any, List
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class ReasoningAgent:
    """
    Agent that synthesizes the final answer from all gathered information
    """
    
    def __init__(self):
        """Initialize reasoning agent"""
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=config.TEMPERATURE
        )
        
        self.reasoning_prompt = PromptTemplate(
            input_variables=["question", "search_info", "retrieved_info", "document_info"],
            template="""You are a reasoning agent for a research assistant. Your task is to synthesize a comprehensive answer from all available information.

Research Question: {question}

Information from Web Search:
{search_info}

Information from Knowledge Base:
{retrieved_info}

Information from Documents:
{document_info}

Your task:
1. Analyze all the information provided
2. Synthesize a comprehensive, well-structured answer
3. Ensure the answer directly addresses the research question
4. Include proper citations and sources
5. If information is conflicting, note the different perspectives
6. If information is insufficient, acknowledge limitations

Provide a detailed, well-reasoned answer with proper source citations.

Answer:
"""
        )
    
    def synthesize_answer(
        self,
        question: str,
        search_info: str = "",
        retrieved_info: str = "",
        document_info: str = ""
    ) -> Dict[str, Any]:
        """
        Synthesize final answer from all information
        
        Args:
            question: Research question
            search_info: Information from web search
            retrieved_info: Information from vector store
            document_info: Information from documents
            
        Returns:
            Dictionary with 'answer' and 'reasoning'
        """
        # Prepare information strings
        search_str = search_info or "No web search information available."
        retrieved_str = retrieved_info or "No information retrieved from knowledge base."
        document_str = document_info or "No document information available."
        
        # Generate answer
        try:
            prompt = self.reasoning_prompt.format(
                question=question,
                search_info=search_str,
                retrieved_info=retrieved_str,
                document_info=document_str
            )
            
            answer = self.llm.invoke(prompt)
            
            return {
                "answer": answer,
                "reasoning": "Synthesized from all available information sources.",
                "sources_used": {
                    "web_search": bool(search_info),
                    "knowledge_base": bool(retrieved_info),
                    "documents": bool(document_info)
                }
            }
        
        except Exception as e:
            print(f"Reasoning agent error: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "reasoning": "Failed to synthesize answer due to error.",
                "sources_used": {}
            }

