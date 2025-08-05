"""
Conversation Manager for Personal Agent

This module contains the ConversationManager class that handles conversation state,
history management, and related operations.
"""

from typing import List, Dict, Any, Optional
from .state import ConversationState
from ..utils.common import generate_id
from ..memory.models import MemoryItem
from ..memory.storage import MemoryStorage


class ConversationManager:
    """
    Manages conversation state, history, and related operations.
    """
    
    def __init__(self, user_id: str = "default_user", memory_storage: MemoryStorage = None):
        """
        Initialize the conversation manager.
        
        Args:
            user_id (str): ID of the user interacting with the agent
            memory_storage (MemoryStorage): Memory storage instance
        """
        self.user_id = user_id
        self.memory_storage = memory_storage
        self.conversation_history = []
        self.conversation_id = generate_id()
        self.state = ConversationState.IN_PROGRESS
        self.clarification_context = {}
    
    def add_user_message(self, content: str, message_id: str = None) -> Dict[str, Any]:
        """
        Add a user message to the conversation history.
        
        Args:
            content (str): The user's message content
            message_id (str): Optional message ID
            
        Returns:
            Dict[str, Any]: The added message object
        """
        message = {
            "role": "user",
            "content": content,
            "id": message_id or generate_id()
        }
        self.conversation_history.append(message)
        return message
    
    def add_agent_message(self, content: str, message_id: str = None) -> Dict[str, Any]:
        """
        Add an agent message to the conversation history.
        
        Args:
            content (str): The agent's message content
            message_id (str): Optional message ID
            
        Returns:
            Dict[str, Any]: The added message object
        """
        message = {
            "role": "assistant",
            "content": content,
            "id": message_id or generate_id()
        }
        self.conversation_history.append(message)
        return message
    
    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history.
        
        Args:
            limit (int): Maximum number of messages to retrieve
            
        Returns:
            List[Dict[str, Any]]: Recent conversation history
        """
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def save_conversation_turn(self, user_input: str, agent_response: str) -> bool:
        """
        Save a conversation turn to memory.
        
        Args:
            user_input (str): User's input message
            agent_response (str): Agent's response
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.memory_storage:
            return False
        
        # Create memory item for conversation turn
        memory_item = MemoryItem(
            type="conversation",
            content={
                "conversation_id": self.conversation_id,
                "user_id": self.user_id,
                "turns": [
                    {
                        "role": "user",
                        "content": user_input
                    },
                    {
                        "role": "assistant",
                        "content": agent_response
                    }
                ]
            }
        )
        
        return self.memory_storage.save(memory_item)
    
    def is_exit_command(self, user_input: str) -> bool:
        """
        Check if the user input is an exit command.
        
        Args:
            user_input (str): The user input to check
            
        Returns:
            bool: True if it's an exit command, False otherwise
        """
        return user_input.lower() in ['quit', 'exit', 'bye']
    
    def set_state(self, state: ConversationState) -> None:
        """
        Set the conversation state.
        
        Args:
            state (ConversationState): The new conversation state
        """
        self.state = state
    
    def get_state(self) -> ConversationState:
        """
        Get the current conversation state.
        
        Returns:
            ConversationState: The current conversation state
        """
        return self.state
    
    def update_clarification_context(self, key: str, value: Any) -> None:
        """
        Update the clarification context.
        
        Args:
            key (str): The context key
            value (Any): The context value
        """
        self.clarification_context[key] = value
    
    def get_clarification_context(self, key: str = None) -> Any:
        """
        Get clarification context.
        
        Args:
            key (str): Optional key to retrieve specific context
            
        Returns:
            Any: The requested context or entire context dict
        """
        if key:
            return self.clarification_context.get(key)
        return self.clarification_context
    
    def clear_clarification_context(self) -> None:
        """
        Clear the clarification context.
        """
        self.clarification_context.clear()