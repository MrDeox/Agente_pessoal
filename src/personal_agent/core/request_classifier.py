"""
Request Classifier for Personal Agent

This module contains the RequestClassifier class that handles classification of
user requests into different categories such as planning, reasoning, decision tree, etc.
"""

from typing import List, Dict, Any, Optional


class RequestClassifier:
    """
    Classifies user requests into different categories for appropriate handling.
    """
    
    def __init__(self):
        """
        Initialize the request classifier.
        """
        # Define keywords for different request types
        self.planning_keywords = [
            "plan", "schedule", "organize", "break down", "steps to",
            "how to", "need to do", "tasks for", "project plan"
        ]
        
        self.reasoning_keywords = [
            "reason", "think", "conclude", "deduce", "infer",
            "logic", "conclusion", "because", "therefore", "thus"
        ]
        
        self.decision_tree_keywords = [
            "decide", "choose", "select", "pick", "which one",
            "what should I do", "conflict", "schedule", "priority"
        ]
    
    def is_planning_request(self, user_input: str) -> bool:
        """
        Check if the user input is a planning request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            bool: True if it's a planning request, False otherwise
        """
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in self.planning_keywords)
    
    def is_reasoning_request(self, user_input: str) -> bool:
        """
        Check if the user input is a reasoning request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            bool: True if it's a reasoning request, False otherwise
        """
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in self.reasoning_keywords)
    
    def is_decision_tree_request(self, user_input: str) -> bool:
        """
        Check if the user input is a decision tree request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            bool: True if it's a decision tree request, False otherwise
        """
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in self.decision_tree_keywords)
    
    def classify_request(self, user_input: str) -> str:
        """
        Classify a user request into a category.
        
        Args:
            user_input (str): The user input
            
        Returns:
            str: The request category ("planning", "reasoning", "decision_tree", or "general")
        """
        if self.is_planning_request(user_input):
            return "planning"
        elif self.is_reasoning_request(user_input):
            return "reasoning"
        elif self.is_decision_tree_request(user_input):
            return "decision_tree"
        else:
            return "general"
    
    def get_keywords_for_category(self, category: str) -> List[str]:
        """
        Get keywords for a specific category.
        
        Args:
            category (str): The category name
            
        Returns:
            List[str]: List of keywords for the category
        """
        keyword_map = {
            "planning": self.planning_keywords,
            "reasoning": self.reasoning_keywords,
            "decision_tree": self.decision_tree_keywords
        }
        return keyword_map.get(category, [])