"""
Memory Models for Personal Agent

This module contains the data models for representing memory items and conversations.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


@dataclass
class Entity:
    """Represents an entity extracted from text."""
    id: str
    type: str  # person, organization, location, date, etc.
    value: str
    confidence: float
    metadata: Dict[str, Any] = None


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float
    metadata: Dict[str, Any] = None


@dataclass
class MemoryItem:
    id: str = None
    type: str = "conversation"  # conversation, knowledge, task, skill
    content: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    embedding: Optional[list] = None  # For semantic search
    entities: List[Entity] = None
    relationships: List[Relationship] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.content is None:
            self.content = {}
        if self.metadata is None:
            self.metadata = {}
        if self.entities is None:
            self.entities = []
        if self.relationships is None:
            self.relationships = []


@dataclass
class ConversationTurn:
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    entities: List[Entity] = None
    relationships: List[Relationship] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.entities is None:
            self.entities = []
        if self.relationships is None:
            self.relationships = []


@dataclass
class Conversation:
    id: str = None
    user_id: str = None
    turns: List[ConversationTurn] = None
    created_at: datetime = None
    updated_at: datetime = None
    entities: List[Entity] = None
    relationships: List[Relationship] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.turns is None:
            self.turns = []
        if self.entities is None:
            self.entities = []
        if self.relationships is None:
            self.relationships = []


@dataclass
class Feedback:
    id: str = None
    user_id: str = None
    conversation_id: str = None
    message_id: str = None  # ID of the agent's response being rated
    rating: int = None  # Rating scale (e.g., 1-5)
    feedback_type: str = "rating"  # rating, thumbs_up_down, comment
    comment: Optional[str] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}