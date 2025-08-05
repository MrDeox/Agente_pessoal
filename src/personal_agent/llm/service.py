"""
LLM Service for Personal Agent

This module contains the LLMService class that manages all LLM-related operations,
including response generation, context creation, and model management.
"""

from typing import List, Dict, Any, Optional
from ..llm.client import LLMClient
from ..llm.models import Message
from ..config.settings import Config
from ..context.processor import ContextProcessor
from ..utils.logging import get_logger
from ..llm.exceptions import LLMException


class LLMService:
    """
    Manages all LLM-related operations for the agent.
    """
    
    def __init__(self, config: Config = None, llm_client: LLMClient = None):
        """
        Initialize the LLM service.
        
        Args:
            config (Config): Configuration object
            llm_client (LLMClient): LLM client instance
        """
        self.config = config or Config.load()
        try:
            self.client = llm_client or LLMClient(self.config)
        except Exception as e:
            logger = get_logger()
            logger.warning(f"Could not initialize LLM client: {e}")
            self.client = None
        self.context_processor = ContextProcessor()
        self.logger = get_logger()
    
    def generate_response(self, user_input: str, conversation_history: List[Dict[str, str]], 
                         memory_context: str = "") -> str:
        """
        Generate a response using the LLM client.
        
        Args:
            user_input (str): The user's input
            conversation_history (List[Dict[str, str]]): Recent conversation history
            memory_context (str): Context retrieved from memory
            
        Returns:
            str: The LLM-generated response
            
        Raises:
            LLMException: If there's an error with the LLM
        """
        if not self.client:
            raise LLMException("LLM client not initialized")
        
        # Use context processor to create context-aware prompt if available
        if self.context_processor:
            messages = self.context_processor.create_context_aware_prompt(
                user_input=user_input,
                conversation_history=conversation_history,
                memory_context=memory_context
            )
        else:
            # Fallback to original method
            messages = []
            
            # Add memory context if available
            if memory_context:
                messages.append(Message(
                    role="system",
                    content=f"Use the following conversation history as context:\n{memory_context}"
                ))
            
            # Add recent conversation history (limit to last 5 turns)
            for turn in conversation_history[-10:]:  # Last 5 turns (10 messages)
                messages.append(Message(
                    role=turn["role"],
                    content=turn["content"]
                ))
            
            # Add the current user input
            messages.append(Message(
                role="user",
                content=user_input
            ))
        
        # Generate response from LLM
        try:
            self.logger.info(f"Generating LLM response with {len(messages)} messages")
            response = self.client.generate_response(messages)
            self.logger.info("LLM response generated successfully")
            return response.content
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """
        Check if the LLM service is properly initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self.client is not None
    
    def get_client(self) -> Optional[LLMClient]:
        """
        Get the LLM client instance.
        
        Returns:
            Optional[LLMClient]: The LLM client instance or None if not initialized
        """
        return self.client