"""
Enhanced Conversation Interface for Personal Agent

This module provides an enhanced interface for natural conversation flow.
"""

from typing import Optional, Dict, Any, List
from .state import ConversationStateManager, ConversationState, DialogueAct
from .dialogue_act import DialogueActRecognizer, dialogue_act_recognizer
from .response_generator import ResponseGenerator, response_generator
from .ambiguity_detector import AmbiguityDetector, ambiguity_detector
from .question_generator import QuestionGenerator, question_generator
from ..llm.models import Message
import re
import random


class EnhancedConversationInterface:
    """Enhanced interface for natural conversation flow."""
    
    def __init__(self, user_id: str):
        """
        Initialize the enhanced conversation interface.
        
        Args:
            user_id (str): ID of the user
        """
        self.state_manager = ConversationStateManager(user_id)
        self.dialogue_recognizer = dialogue_act_recognizer
        self.response_generator = response_generator
        self.ambiguity_detector = ambiguity_detector
        self.question_generator = question_generator
        self.conversation_history: List[Dict[str, str]] = []
        self.ambiguity_threshold = 0.6  # Minimum confidence to consider an ambiguity
    
    def process_input(self, user_input: str, llm_response: str = None) -> str:
        """
        Process user input and generate an enhanced response.
        
        Args:
            user_input (str): User's input
            llm_response (str): Raw LLM response (if available)
            
        Returns:
            str: Enhanced response
        """
        # Update conversation context
        self.state_manager.update_context(
            last_user_input=user_input,
            turn_count=self.state_manager.get_context().turn_count + 1
        )
        
        # Recognize dialogue act
        dialogue_act, confidence = self.dialogue_recognizer.recognize_act(user_input)
        self.state_manager.update_dialogue_act(dialogue_act)
        
        # Check for ambiguities in user input
        ambiguities = self.ambiguity_detector.detect_ambiguities(user_input)
        high_confidence_ambiguities = [
            amb for amb in ambiguities
            if amb.confidence >= self.ambiguity_threshold
        ]
        
        # If we have high-confidence ambiguities, ask for clarification
        if high_confidence_ambiguities:
            # Generate clarification questions
            questions = self.question_generator.generate_multiple_questions(
                high_confidence_ambiguities,
                max_questions=2,  # Limit to 2 questions to avoid overwhelming the user
                context=self.get_conversation_context()
            )
            
            # Combine questions into a single response
            if len(questions) == 1:
                enhanced_response = questions[0]
            else:
                # Format multiple questions as a list
                question_list = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(questions)])
                enhanced_response = f"I'd like to clarify a few things:\n{question_list}"
            
            # Update conversation state to indicate we're asking for clarification
            self.state_manager.update_state(ConversationState.ASKING_CLARIFICATION, "ambiguity_detected")
        else:
            # Update conversation state based on dialogue act
            self._update_conversation_state(dialogue_act)
            
            # Generate enhanced response
            if llm_response:
                enhanced_response = self.response_generator.generate_response(
                    user_input,
                    llm_response,
                    self.state_manager,
                    dialogue_act
                )
            else:
                # Generate a template-based response if no LLM response is available
                enhanced_response = self._generate_template_response(dialogue_act)
        
        # Update context with agent response
        self.state_manager.update_context(last_agent_response=enhanced_response)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": enhanced_response})
        
        return enhanced_response
    
    def _update_conversation_state(self, dialogue_act: DialogueAct) -> None:
        """
        Update conversation state based on dialogue act.
        
        Args:
            dialogue_act (DialogueAct): Recognized dialogue act
        """
        current_state = self.state_manager.get_context().state
        trigger = f"dialogue_act:{dialogue_act.value}"
        
        # State transition logic
        if dialogue_act == DialogueAct.GREETING:
            if current_state == ConversationState.INITIAL:
                self.state_manager.update_state(ConversationState.GREETING, trigger)
            else:
                self.state_manager.update_state(ConversationState.IN_PROGRESS, trigger)
        
        elif dialogue_act == DialogueAct.CLOSING:
            self.state_manager.update_state(ConversationState.CLOSING, trigger)
        
        elif dialogue_act == DialogueAct.CLARIFICATION:
            self.state_manager.update_state(ConversationState.ASKING_CLARIFICATION, trigger)
        
        elif dialogue_act == DialogueAct.CONFIRMATION:
            self.state_manager.update_state(ConversationState.SEEKING_CONFIRMATION, trigger)
        
        elif dialogue_act in [DialogueAct.QUESTION, DialogueAct.REQUEST]:
            self.state_manager.update_state(ConversationState.PROVIDING_INFORMATION, trigger)
        
        elif current_state == ConversationState.INITIAL:
            self.state_manager.update_state(ConversationState.IN_PROGRESS, trigger)
    
    def _generate_template_response(self, dialogue_act: DialogueAct) -> str:
        """
        Generate a template-based response when no LLM response is available.
        
        Args:
            dialogue_act (DialogueAct): Recognized dialogue act
            
        Returns:
            str: Template-based response
        """
        context = self.state_manager.get_context()
        
        # Get appropriate template based on dialogue act and state
        template_key = (dialogue_act, context.state)
        templates = self.response_generator.response_templates.get(template_key)
        
        if templates:
            return random.choice(templates)
        
        # Fallback templates
        fallback_templates = {
            DialogueAct.GREETING: ["Hello! How can I help you today?"],
            DialogueAct.QUESTION: ["That's an interesting question."],
            DialogueAct.REQUEST: ["I'll help you with that."],
            DialogueAct.STATEMENT: ["I see. Tell me more."],
            DialogueAct.CLOSING: ["Goodbye! Have a great day!"],
            DialogueAct.ERROR: ["I'm sorry, I didn't understand that."]
        }
        
        templates = fallback_templates.get(dialogue_act, ["I'm here to help. What can I do for you?"])
        return random.choice(templates)
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dict[str, Any]: Current conversation context
        """
        context = self.state_manager.get_context()
        return {
            "state": context.state.value,
            "dialogue_act": context.dialogue_act.value,
            "topic": context.topic,
            "turn_count": context.turn_count,
            "last_user_input": context.last_user_input,
            "last_agent_response": context.last_agent_response
        }
    
    def get_state_description(self) -> str:
        """
        Get a human-readable description of the current conversation state.
        
        Returns:
            str: Description of current state
        """
        context = self.state_manager.get_context()
        state_descriptions = {
            ConversationState.INITIAL: "Conversation is starting",
            ConversationState.GREETING: "Exchanging greetings",
            ConversationState.IN_PROGRESS: "Ongoing conversation",
            ConversationState.ASKING_CLARIFICATION: "Asking for clarification",
            ConversationState.PROVIDING_INFORMATION: "Providing information",
            ConversationState.SEEKING_CONFIRMATION: "Seeking confirmation",
            ConversationState.CLOSING: "Ending conversation",
            ConversationState.ERROR: "Error state"
        }
        
        return state_descriptions.get(context.state, "Unknown state")
    
    def reset_conversation(self) -> None:
        """Reset the conversation to initial state."""
        self.state_manager.reset_conversation()
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation so far.
        
        Returns:
            str: Conversation summary
        """
        context = self.state_manager.get_context()
        return (f"Conversation with {context.user_id}, "
                f"{context.turn_count} turns, "
                f"current state: {context.state.value}, "
                f"current topic: {context.topic or 'not set'}")


# Convenience function for backward compatibility
def create_enhanced_interface(user_id: str) -> EnhancedConversationInterface:
    """
    Create an enhanced conversation interface.
    
    Args:
        user_id (str): ID of the user
        
    Returns:
        EnhancedConversationInterface: New interface instance
    """
    return EnhancedConversationInterface(user_id)