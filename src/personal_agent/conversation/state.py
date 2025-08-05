"""
Conversation State Management for Personal Agent

This module provides functionality for managing conversation state to enable more natural dialogue flow.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime


class ConversationState(Enum):
    """Enumeration of possible conversation states."""
    INITIAL = "initial"
    GREETING = "greeting"
    IN_PROGRESS = "in_progress"
    ASKING_CLARIFICATION = "asking_clarification"
    PROVIDING_INFORMATION = "providing_information"
    SEEKING_CONFIRMATION = "seeking_confirmation"
    CLOSING = "closing"
    ERROR = "error"


class DialogueAct(Enum):
    """Enumeration of dialogue acts."""
    GREETING = "greeting"
    QUESTION = "question"
    STATEMENT = "statement"
    REQUEST = "request"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"
    ACKNOWLEDGMENT = "acknowledgment"
    CLOSING = "closing"
    ERROR = "error"


@dataclass
class ConversationContext:
    """Represents the context of a conversation."""
    user_id: str
    conversation_id: str
    state: ConversationState = ConversationState.INITIAL
    previous_state: ConversationState = ConversationState.INITIAL
    dialogue_act: DialogueAct = DialogueAct.GREETING
    topic: str = ""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    user_intent: str = ""
    last_user_input: str = ""
    last_agent_response: str = ""
    turn_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTransition:
    """Represents a transition between conversation states."""
    from_state: ConversationState
    to_state: ConversationState
    trigger: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationStateManager:
    """Manages conversation state throughout the dialogue."""
    
    def __init__(self, user_id: str):
        """
        Initialize the conversation state manager.
        
        Args:
            user_id (str): ID of the user
        """
        self.user_id = user_id
        self.conversation_id = self._generate_conversation_id()
        self.context = ConversationContext(user_id=user_id, conversation_id=self.conversation_id)
        self.state_history: List[StateTransition] = []
        self.max_history_length = 10
    
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        import uuid
        return str(uuid.uuid4())
    
    def update_state(self, new_state: ConversationState, trigger: str = "") -> bool:
        """
        Update the conversation state.
        
        Args:
            new_state (ConversationState): The new state to transition to
            trigger (str): What triggered the state change
            
        Returns:
            bool: True if state was updated, False otherwise
        """
        if new_state == self.context.state:
            return False
        
        # Record the state transition
        transition = StateTransition(
            from_state=self.context.state,
            to_state=new_state,
            trigger=trigger
        )
        self.state_history.append(transition)
        
        # Limit history length
        if len(self.state_history) > self.max_history_length:
            self.state_history = self.state_history[-self.max_history_length:]
        
        # Update context
        self.context.previous_state = self.context.state
        self.context.state = new_state
        self.context.updated_at = datetime.now()
        
        return True
    
    def update_dialogue_act(self, act: DialogueAct) -> bool:
        """
        Update the current dialogue act.
        
        Args:
            act (DialogueAct): The new dialogue act
            
        Returns:
            bool: True if dialogue act was updated, False otherwise
        """
        if act == self.context.dialogue_act:
            return False
        
        self.context.dialogue_act = act
        self.context.updated_at = datetime.now()
        return True
    
    def update_context(self, **kwargs) -> bool:
        """
        Update context information.
        
        Args:
            **kwargs: Context attributes to update
            
        Returns:
            bool: True if context was updated, False otherwise
        """
        updated = False
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
                updated = True
        
        if updated:
            self.context.updated_at = datetime.now()
        
        return updated
    
    def get_context(self) -> ConversationContext:
        """
        Get the current conversation context.
        
        Returns:
            ConversationContext: Current conversation context
        """
        return self.context
    
    def get_state_history(self) -> List[StateTransition]:
        """
        Get the state transition history.
        
        Returns:
            List[StateTransition]: State transition history
        """
        return self.state_history
    
    def reset_conversation(self) -> None:
        """Reset the conversation to initial state."""
        self.conversation_id = self._generate_conversation_id()
        self.context = ConversationContext(user_id=self.user_id, conversation_id=self.conversation_id)
        self.state_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation state to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the conversation state
        """
        return {
            "user_id": self.context.user_id,
            "conversation_id": self.context.conversation_id,
            "state": self.context.state.value,
            "previous_state": self.context.previous_state.value,
            "dialogue_act": self.context.dialogue_act.value,
            "topic": self.context.topic,
            "entities": self.context.entities,
            "user_intent": self.context.user_intent,
            "last_user_input": self.context.last_user_input,
            "last_agent_response": self.context.last_agent_response,
            "turn_count": self.context.turn_count,
            "created_at": self.context.created_at.isoformat(),
            "updated_at": self.context.updated_at.isoformat(),
            "metadata": self.context.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationStateManager':
        """
        Create a ConversationStateManager from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation
            
        Returns:
            ConversationStateManager: New instance
        """
        manager = cls(data["user_id"])
        manager.context.conversation_id = data["conversation_id"]
        manager.context.state = ConversationState(data["state"])
        manager.context.previous_state = ConversationState(data["previous_state"])
        manager.context.dialogue_act = DialogueAct(data["dialogue_act"])
        manager.context.topic = data["topic"]
        manager.context.entities = data["entities"]
        manager.context.user_intent = data["user_intent"]
        manager.context.last_user_input = data["last_user_input"]
        manager.context.last_agent_response = data["last_agent_response"]
        manager.context.turn_count = data["turn_count"]
        manager.context.created_at = datetime.fromisoformat(data["created_at"])
        manager.context.updated_at = datetime.fromisoformat(data["updated_at"])
        manager.context.metadata = data["metadata"]
        return manager