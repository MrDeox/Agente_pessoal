"""
Response Processor for Personal Agent

This module contains the ResponseProcessor class that handles response enhancement,
adaptation based on feedback, and other response-related operations.
"""

from typing import Dict, Any, Optional
from ..conversation.interface import EnhancedConversationInterface
from ..core.feedback import FeedbackSystem
from ..utils.logging import get_logger


class ResponseProcessor:
    """
    Handles response enhancement, adaptation, and related operations.
    """
    
    def __init__(self, user_id: str = "default_user", feedback_system: FeedbackSystem = None):
        """
        Initialize the response processor.
        
        Args:
            user_id (str): ID of the user interacting with the agent
            feedback_system (FeedbackSystem): Feedback system instance
        """
        self.user_id = user_id
        self.feedback_system = feedback_system or FeedbackSystem(user_id=user_id)
        self.conversation_interface = EnhancedConversationInterface(user_id)
        self.logger = get_logger()
    
    def enhance_response(self, user_input: str, raw_response: str) -> str:
        """
        Enhance a raw response using the conversation interface.
        
        Args:
            user_input (str): The user's input
            raw_response (str): The raw response from the LLM or other source
            
        Returns:
            str: The enhanced response
        """
        try:
            return self.conversation_interface.process_input(user_input, raw_response)
        except Exception as e:
            self.logger.warning(f"Error enhancing response: {e}")
            # Return raw response if enhancement fails
            return raw_response
    
    def adapt_response_based_on_feedback(self, response: str, previous_response_id: str) -> str:
        """
        Adapt a response based on feedback for a previous response.
        
        Args:
            response (str): The current response
            previous_response_id (str): ID of the previous response to check for feedback
            
        Returns:
            str: The adapted response if feedback suggests adaptation, otherwise the original response
        """
        try:
            if self.feedback_system.should_adapt_response(previous_response_id):
                adaptation_suggestion = self.feedback_system.get_adaptation_suggestion(previous_response_id)
                if adaptation_suggestion:
                    # Add adaptation suggestion to the response
                    return f"[Adapted based on feedback: {adaptation_suggestion}] {response}"
        except Exception as e:
            self.logger.warning(f"Error adapting response based on feedback: {e}")
        
        return response
    
    def get_welcome_message(self) -> str:
        """
        Generate a welcome message for new conversations.
        
        Returns:
            str: Welcome message
        """
        try:
            welcome_input = "Hello"
            raw_welcome = f"Hello! I'm your personal assistant. How can I help you today? Type 'quit' to exit."
            return self.conversation_interface.process_input(welcome_input, raw_welcome)
        except Exception as e:
            self.logger.warning(f"Error generating welcome message: {e}")
            return "Hello! How can I help you today?"
    
    def get_feedback_system(self) -> FeedbackSystem:
        """
        Get the feedback system instance.
        
        Returns:
            FeedbackSystem: The feedback system instance
        """
        return self.feedback_system
    
    def collect_rating_feedback(self, message_id: str, rating: int, 
                               conversation_id: str = None, comment: str = None) -> bool:
        """
        Collect rating feedback for a specific message.
        
        Args:
            message_id (str): ID of the message being rated
            rating (int): Rating value (typically 1-5)
            conversation_id (str): Optional conversation ID
            comment (str): Optional comment about the feedback
            
        Returns:
            bool: True if feedback was saved successfully, False otherwise
        """
        try:
            return self.feedback_system.collect_rating_feedback(
                message_id=message_id,
                rating=rating,
                conversation_id=conversation_id,
                comment=comment
            )
        except Exception as e:
            self.logger.error(f"Error collecting rating feedback: {e}")
            return False
    
    def collect_thumbs_feedback(self, message_id: str, is_positive: bool,
                               conversation_id: str = None, comment: str = None) -> bool:
        """
        Collect thumbs up/down feedback for a specific message.
        
        Args:
            message_id (str): ID of the message being rated
            is_positive (bool): True for thumbs up, False for thumbs down
            conversation_id (str): Optional conversation ID
            comment (str): Optional comment about the feedback
            
        Returns:
            bool: True if feedback was saved successfully, False otherwise
        """
        try:
            return self.feedback_system.collect_thumbs_feedback(
                message_id=message_id,
                is_positive=is_positive,
                conversation_id=conversation_id,
                comment=comment
            )
        except Exception as e:
            self.logger.error(f"Error collecting thumbs feedback: {e}")
            return False
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Get feedback statistics for the current user.
        
        Returns:
            Dict[str, Any]: Feedback statistics
        """
        try:
            return self.feedback_system.get_feedback_statistics()
        except Exception as e:
            self.logger.error(f"Error retrieving feedback statistics: {e}")
            return {}