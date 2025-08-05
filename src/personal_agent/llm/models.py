"""
Data Models for LLM Integration

This module contains the data models used for LLM interactions.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""
    content: str
    finish_reason: str
    usage: Dict[str, int]  # tokens used
    model: str