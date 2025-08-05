"""
Conversation Module for Personal Agent

This module contains components for managing conversation state, recognizing dialogue acts,
and generating more natural responses.
"""

from .state import (
    ConversationStateManager,
    ConversationState,
    DialogueAct,
    ConversationContext,
    StateTransition
)

from .dialogue_act import (
    DialogueActRecognizer,
    dialogue_act_recognizer
)

from .response_generator import (
    ResponseGenerator,
    response_generator
)

from .interface import (
    EnhancedConversationInterface,
    create_enhanced_interface
)

__all__ = [
    "ConversationStateManager",
    "ConversationState",
    "DialogueAct",
    "ConversationContext",
    "StateTransition",
    "DialogueActRecognizer",
    "dialogue_act_recognizer",
    "ResponseGenerator",
    "response_generator",
    "EnhancedConversationInterface",
    "create_enhanced_interface"
]