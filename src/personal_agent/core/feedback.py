"""
Feedback System for Personal Agent

This module contains the feedback system that allows the agent to learn from user feedback.
"""

from typing import Optional, Dict, Any, List
from ..memory.storage import SQLiteMemoryStorage
from ..memory.models import Feedback
from ..config.settings import Config
from ..utils.validation import (
    validate_message_id, validate_rating, validate_feedback_comment, ValidationError
)
from ..utils.logging import get_logger, log_exception
from ..utils.common import generate_id


class FeedbackSystem:
    """
    Feedback system that handles collection, storage, and analysis of user feedback.
    """
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize the feedback system.
        
        Args:
            user_id (str): ID of the user interacting with the agent
        """
        self.user_id = user_id
        self.storage = SQLiteMemoryStorage()
        self.config = Config.load()
        
        # Feedback configuration
        self.rating_scale = self.config.feedback.rating_scale
        self.feedback_types = ["rating", "thumbs_up_down", "comment"]
    
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
        # Validate inputs
        try:
            validated_message_id = validate_message_id(message_id)
            validated_rating = validate_rating(rating, 1, self.rating_scale)
            validated_comment = validate_feedback_comment(comment) if comment else None
            # conversation_id is optional, so we don't validate it
        except ValidationError as e:
            logger = get_logger()
            logger.warning(f"Feedback validation error: {e}")
            return False
        
        # Create feedback object
        feedback = Feedback(
            user_id=self.user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            rating=rating,
            feedback_type="rating",
            comment=comment
        )
        
        # Save feedback
        logger = get_logger()
        try:
            logger.info(f"Saving rating feedback for message {validated_message_id}")
            result = self.storage.save_feedback(feedback)
            if result:
                logger.info("Rating feedback saved successfully")
            else:
                logger.warning("Failed to save rating feedback")
            return result
        except Exception as e:
            log_exception(e, "Feedback saving")
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
        # Validate inputs
        try:
            validated_message_id = validate_message_id(message_id)
            validated_comment = validate_feedback_comment(comment) if comment else None
            # conversation_id is optional, so we don't validate it
        except ValidationError as e:
            logger = get_logger()
            logger.warning(f"Feedback validation error: {e}")
            return False
        
        # Convert thumbs feedback to rating (1 for thumbs down, 5 for thumbs up)
        rating = 5 if is_positive else 1
        
        # Create feedback object
        feedback = Feedback(
            user_id=self.user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            rating=rating,
            feedback_type="thumbs_up_down",
            comment=comment
        )
        
        # Save feedback
        logger = get_logger()
        try:
            logger.info(f"Saving thumbs feedback for message {validated_message_id}")
            result = self.storage.save_feedback(feedback)
            if result:
                logger.info("Thumbs feedback saved successfully")
            else:
                logger.warning("Failed to save thumbs feedback")
            return result
        except Exception as e:
            log_exception(e, "Thumbs feedback saving")
            return False
    
    def get_feedback_for_message(self, message_id: str) -> Optional[Feedback]:
        """
        Retrieve feedback for a specific message.
        
        Args:
            message_id (str): ID of the message
            
        Returns:
            Optional[Feedback]: Feedback object if found, None otherwise
        """
        return self.storage.get_feedback(message_id)
    
    def get_user_feedback_history(self, limit: int = 50) -> List[Feedback]:
        """
        Get feedback history for the current user.
        
        Args:
            limit (int): Maximum number of feedback items to retrieve
            
        Returns:
            List[Feedback]: List of feedback items
        """
        return self.storage.get_user_feedback_history(self.user_id, limit)
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Get feedback statistics for the current user.
        
        Returns:
            Dict[str, Any]: Feedback statistics
        """
        return self.storage.get_feedback_stats(self.user_id)
    
    def should_adapt_response(self, message_id: str) -> bool:
        """
        Determine if the agent should adapt its response based on feedback.
        
        Args:
            message_id (str): ID of the message to check
            
        Returns:
            bool: True if the agent should adapt, False otherwise
        """
        if not self.config.feedback.enabled:
            return False
            
        feedback = self.get_feedback_for_message(message_id)
        if not feedback:
            return False
        
        # Adaptation logic based on configuration threshold
        return feedback.rating <= self.config.feedback.adapt_threshold
    
    def get_adaptation_suggestion(self, message_id: str) -> Optional[str]:
        """
        Get a suggestion for how to adapt the response based on feedback.
        
        Args:
            message_id (str): ID of the message to get adaptation for
            
        Returns:
            Optional[str]: Suggestion for adaptation, None if no adaptation needed
        """
        feedback = self.get_feedback_for_message(message_id)
        if not feedback:
            return None
        
        # Simple adaptation suggestions based on rating
        if feedback.rating == 1:
            return "The response was not helpful. Try providing more direct information."
        elif feedback.rating == 2:
            return "The response could be improved. Consider being more specific."
        elif feedback.comment:
            return f"User comment: {feedback.comment}"
        
        return None