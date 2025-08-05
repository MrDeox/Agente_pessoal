"""
Dialogue Act Recognition for Personal Agent

This module provides functionality for recognizing dialogue acts to enable more natural conversation flow.
"""

from typing import List, Dict, Tuple
import re
from enum import Enum
from .state import DialogueAct


class DialogueActRecognizer:
    """Recognizes dialogue acts from user input."""
    
    def __init__(self):
        """Initialize the dialogue act recognizer."""
        # Define patterns for different dialogue acts
        self.patterns = {
            DialogueAct.GREETING: [
                r'\b(hello|hi|hey|good\s+(morning|afternoon|evening))\b',
                r'\bhowdy\b',
                r'\bwhat\'?s\s+up\b'
            ],
            DialogueAct.CLOSING: [
                r'\b(bye|goodbye|see\s+you|farewell|quit|exit)\b',
                r'\b(that\'?s\s+all|that\'?s\s+it)\b'
            ],
            DialogueAct.QUESTION: [
                r'\b(what|where|when|why|how|who|which|whose|whom)\b.*\?',
                r'\b(could|would|can|will|shall|do|does|did|is|are|was|were)\b.*\?',
                r'.*\?$'
            ],
            DialogueAct.REQUEST: [
                r'\b(please|could you|would you|can you|help me)\b',
                r'\b(i need|i want|i would like)\b',
                r'\b(tell me|show me|give me|find me)\b'
            ],
            DialogueAct.CONFIRMATION: [
                r'\b(yes|yeah|yep|sure|ok|okay|right|correct|affirmative)\b',
                r'\b(no|nope|negative)\b'
            ],
            DialogueAct.CLARIFICATION: [
                r'\b(what do you mean|can you explain|what exactly|sorry)\b',
                r'\b(i don\'?t understand|i\'?m confused)\b'
            ],
            DialogueAct.ACKNOWLEDGMENT: [
                r'\b(i see|i understand|got it|okay|ok|right)\b',
                r'\b(thanks|thank you|appreciate it)\b'
            ]
        }
    
    def recognize_act(self, text: str) -> Tuple[DialogueAct, float]:
        """
        Recognize the dialogue act from text.
        
        Args:
            text (str): User input text
            
        Returns:
            Tuple[DialogueAct, float]: Recognized dialogue act and confidence score
        """
        text_lower = text.lower().strip()
        
        # Special case for empty text
        if not text_lower:
            return DialogueAct.ERROR, 0.0
        
        # Check each dialogue act pattern
        best_act = DialogueAct.STATEMENT
        best_score = 0.1  # Default low confidence for statement
        
        for act, patterns in self.patterns.items():
            score = self._calculate_pattern_score(text_lower, patterns)
            if score > best_score:
                best_score = score
                best_act = act
        
        return best_act, best_score
    
    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """
        Calculate confidence score based on pattern matching.
        
        Args:
            text (str): Text to match against
            patterns (List[str]): List of regex patterns
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Return higher confidence for exact matches, lower for partial
                if re.fullmatch(pattern, text, re.IGNORECASE):
                    return 0.9
                else:
                    return 0.7
        
        return 0.0
    
    def recognize_multiple_acts(self, text: str, top_n: int = 3) -> List[Tuple[DialogueAct, float]]:
        """
        Recognize multiple possible dialogue acts with confidence scores.
        
        Args:
            text (str): User input text
            top_n (int): Number of top acts to return
            
        Returns:
            List[Tuple[DialogueAct, float]]: List of dialogue acts with confidence scores
        """
        text_lower = text.lower().strip()
        
        if not text_lower:
            return [(DialogueAct.ERROR, 0.0)]
        
        # Calculate scores for all acts
        scores = []
        for act, patterns in self.patterns.items():
            score = self._calculate_pattern_score(text_lower, patterns)
            scores.append((act, score))
        
        # Sort by score and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    
    def get_act_description(self, act: DialogueAct) -> str:
        """
        Get a human-readable description of a dialogue act.
        
        Args:
            act (DialogueAct): The dialogue act
            
        Returns:
            str: Description of the dialogue act
        """
        descriptions = {
            DialogueAct.GREETING: "User is greeting the agent",
            DialogueAct.QUESTION: "User is asking a question",
            DialogueAct.STATEMENT: "User is making a statement",
            DialogueAct.REQUEST: "User is making a request",
            DialogueAct.CONFIRMATION: "User is confirming or denying something",
            DialogueAct.CLARIFICATION: "User is asking for clarification",
            DialogueAct.ACKNOWLEDGMENT: "User is acknowledging or thanking",
            DialogueAct.CLOSING: "User is ending the conversation",
            DialogueAct.ERROR: "Could not determine user intent"
        }
        
        return descriptions.get(act, "Unknown dialogue act")


# Pre-instantiated recognizer for convenience
dialogue_act_recognizer = DialogueActRecognizer()