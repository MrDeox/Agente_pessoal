"""
Response Generator for Personal Agent

This module provides functionality for generating more natural and context-aware responses.
"""

from typing import List, Dict, Any, Optional
from .state import ConversationStateManager, DialogueAct, ConversationState
from ..llm.models import Message
import random
import re


class ResponseGenerator:
    """Generates more natural and context-aware responses."""
    
    def __init__(self):
        """Initialize the response generator."""
        # Templates for different dialogue acts and states
        self.response_templates = {
            (DialogueAct.GREETING, ConversationState.INITIAL): [
                "Hello! I'm your personal assistant. How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?"
            ],
            (DialogueAct.GREETING, ConversationState.IN_PROGRESS): [
                "Hello again! How can I help you further?",
                "Hi! What else can I assist you with?",
                "Welcome back! What would you like to know?"
            ],
            (DialogueAct.QUESTION, ConversationState.IN_PROGRESS): [
                "That's a great question. Let me think about that...",
                "I'd be happy to help with that question.",
                "Let me see if I can answer that for you."
            ],
            (DialogueAct.REQUEST, ConversationState.IN_PROGRESS): [
                "I'll help you with that request.",
                "Sure, I can assist with that.",
                "Let me take care of that for you."
            ],
            (DialogueAct.CLARIFICATION, ConversationState.ASKING_CLARIFICATION): [
                "I apologize for any confusion. Let me clarify that for you.",
                "Let me explain that more clearly.",
                "I see you need more information. Here's a better explanation."
            ],
            (DialogueAct.CONFIRMATION, ConversationState.SEEKING_CONFIRMATION): [
                "Thanks for confirming!",
                "Great, I'll proceed with that.",
                "Perfect, that's helpful to know."
            ],
            (DialogueAct.ACKNOWLEDGMENT, ConversationState.IN_PROGRESS): [
                "I'm glad that was helpful!",
                "You're welcome! Is there anything else I can help with?",
                "Happy to assist! What else would you like to know?"
            ],
            (DialogueAct.CLOSING, ConversationState.CLOSING): [
                "Goodbye! Have a wonderful day!",
                "It was great chatting with you. Take care!",
                "See you later! Feel free to come back anytime."
            ],
            (DialogueAct.ERROR, ConversationState.ERROR): [
                "I'm sorry, I didn't quite understand that. Could you rephrase?",
                "I'm having trouble understanding. Could you try again?",
                "I'm not sure what you mean. Can you explain differently?"
            ]
        }
        
        # Fallback templates for any combination
        self.fallback_templates = [
            "I understand. What else would you like to know?",
            "Thanks for sharing that. How can I help you further?",
            "I see. Is there anything specific you'd like me to help with?",
            "That's interesting. What would you like to do next?",
            "I'm here to help. What else can I assist you with?"
        ]
    
    def generate_response(self, 
                         user_input: str, 
                         llm_response: str, 
                         state_manager: ConversationStateManager,
                         dialogue_act: DialogueAct) -> str:
        """
        Generate a more natural response based on context.
        
        Args:
            user_input (str): The user's input
            llm_response (str): The raw LLM response
            state_manager (ConversationStateManager): Current conversation state
            dialogue_act (DialogueAct): Recognized dialogue act
            
        Returns:
            str: Generated response
        """
        context = state_manager.get_context()
        
        # Get appropriate template based on dialogue act and state
        template_key = (dialogue_act, context.state)
        templates = self.response_templates.get(template_key, self.fallback_templates)
        
        # Select a template (could be enhanced with more sophisticated selection)
        template = random.choice(templates)
        
        # Enhance the response with context-aware elements
        enhanced_response = self._enhance_response(
            template, 
            llm_response, 
            context
        )
        
        return enhanced_response
    
    def _enhance_response(self, 
                         template: str, 
                         llm_response: str, 
                         context: Any) -> str:
        """
        Enhance a response with context-aware elements.
        
        Args:
            template (str): Response template
            llm_response (str): Raw LLM response
            context (Any): Conversation context
            
        Returns:
            str: Enhanced response
        """
        # For now, we'll just combine the template with the LLM response
        # This could be enhanced with more sophisticated techniques
        
        # If the template contains a placeholder for the LLM response, use it
        if "{llm_response}" in template:
            return template.replace("{llm_response}", llm_response)
        
        # Otherwise, combine them naturally
        if llm_response:
            # If template ends with "...", append the LLM response directly
            if template.endswith("..."):
                return template[:-3] + llm_response
            
            # Otherwise, combine with appropriate punctuation
            if template.endswith(('.', '!', '?')):
                return f"{template} {llm_response}"
            else:
                return f"{template}. {llm_response}"
        
        return template
    
    def generate_follow_up_prompt(self, 
                                 context: Any, 
                                 dialogue_act: DialogueAct) -> Optional[str]:
        """
        Generate a follow-up prompt to encourage continued conversation.
        
        Args:
            context (Any): Conversation context
            dialogue_act (DialogueAct): Current dialogue act
            
        Returns:
            Optional[str]: Follow-up prompt or None if not appropriate
        """
        # Don't prompt for follow-up if conversation is closing
        if context.state == ConversationState.CLOSING:
            return None
        
        # Don't prompt for follow-up after acknowledgments or confirmations
        if dialogue_act in [DialogueAct.ACKNOWLEDGMENT, DialogueAct.CONFIRMATION]:
            return None
        
        prompts = [
            "Is there anything else you'd like to know?",
            "What else can I help you with?",
            "Do you have any other questions?",
            "Is there anything more I can assist you with?",
            "What would you like to explore next?"
        ]
        
        return random.choice(prompts)
    
    def adapt_response_style(self, 
                            response: str, 
                            context: Any, 
                            user_preferences: List[str] = None) -> str:
        """
        Adapt response style based on user preferences and conversation history.
        
        Args:
            response (str): Original response
            context (Any): Conversation context
            user_preferences (List[str]): User preferences
            
        Returns:
            str: Adapted response
        """
        # For now, we'll keep it simple
        # This could be enhanced to adapt tone, formality, etc.
        return response
    
    def generate_contextual_intro(self, context: Any) -> str:
        """
        Generate a contextual introduction based on conversation state.
        
        Args:
            context (Any): Conversation context
            
        Returns:
            str: Contextual introduction
        """
        if context.turn_count == 0:
            return random.choice([
                "Hello! I'm your personal assistant. How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?"
            ])
        else:
            # Reference previous conversation topics
            topic_references = [
                "Continuing our conversation",
                "Picking up where we left off",
                "Following up on what we discussed"
            ]
            
            return f"{random.choice(topic_references)}, how can I help you further?"


# Pre-instantiated generator for convenience
response_generator = ResponseGenerator()