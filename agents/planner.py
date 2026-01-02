"""
Planner Agent
Decides what action to take next based on the current state
"""

from typing import Dict, Any, List
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class PlannerAgent:
    """
    Planning agent that decides the next action
    Uses LLaMA-3 via Ollama for decision making
    """
    
    def __init__(self):
        """Initialize planner agent"""
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=config.TEMPERATURE
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["question", "context", "history"],
            template="""You are a planning agent for a research assistant system.

Your task is to decide what action to take next based on:
1. The research question
2. Current context and information gathered
3. Previous actions taken

Available actions:
- SEARCH: Search the web for information (use when you need current information or the question is about recent events)
- READ: Read a document (use when documents are available and relevant)
- RETRIEVE: Retrieve information from the knowledge base (use when you have stored information that might be relevant)
- ANSWER: Provide the final answer (use when you have enough information to answer the question)
- DONE: Task is complete (use when the answer has been provided)

Research Question: {question}

Context Available:
{context}

Previous Actions:
{history}

Based on the above, decide the NEXT action. Consider:
- Do we have enough information to answer? If yes, choose ANSWER
- Do we need current/recent information? If yes, choose SEARCH
- Are there documents to read? If yes, choose READ
- Do we have stored knowledge that might help? If yes, choose RETRIEVE

Respond with ONLY the action name (SEARCH, READ, RETRIEVE, ANSWER, or DONE).
"""
        )
    
    def plan(self, question: str, context: str = "", history: List[str] = None) -> str:
        """
        Decide next action
        
        Args:
            question: Research question
            context: Current context/information
            history: List of previous actions
            
        Returns:
            Action name (SEARCH, READ, RETRIEVE, ANSWER, DONE)
        """
        if history is None:
            history = []
        
        history_str = "\n".join(history) if history else "No previous actions"
        
        prompt = self.prompt_template.format(
            question=question,
            context=context or "No context available yet",
            history=history_str
        )
        
        try:
            response = self.llm.invoke(prompt).strip().upper()
            
            # Validate response
            valid_actions = [
                config.ActionType.SEARCH,
                config.ActionType.READ,
                config.ActionType.RETRIEVE,
                config.ActionType.ANSWER,
                config.ActionType.DONE
            ]
            
            # Extract action from response
            for action in valid_actions:
                if action in response:
                    return action
            
            # Default to SEARCH if unclear
            return config.ActionType.SEARCH
        
        except Exception as e:
            print(f"Planner error: {e}")
            return config.ActionType.SEARCH

