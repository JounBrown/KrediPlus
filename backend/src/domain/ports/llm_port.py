from abc import ABC, abstractmethod


class LLMPort(ABC):
    """
    Port for Large Language Model operations.
    
    This interface allows decoupling from specific LLM providers (OpenAI, Anthropic, etc.)
    To change provider, implement this interface with a new adapter.
    """
    
    @abstractmethod
    async def generate_response(self, query: str, context: str) -> str:
        """
        Generate a response to a query using the provided context.
        
        Args:
            query: The user's question
            context: Relevant context from retrieved documents
            
        Returns:
            Generated response string
            
        Raises:
            Exception: If response generation fails
        """
        pass
    
    @abstractmethod
    async def generate_response_with_system_prompt(
        self, 
        query: str, 
        context: str, 
        system_prompt: str
    ) -> str:
        """
        Generate a response with a custom system prompt.
        
        Args:
            query: The user's question
            context: Relevant context from retrieved documents
            system_prompt: Custom system instructions for the LLM
            
        Returns:
            Generated response string
            
        Raises:
            Exception: If response generation fails
        """
        pass
