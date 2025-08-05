"""
Ambiguity Detection for Personal Agent

This module provides functionality for detecting ambiguous user requests and classifying their types.
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import re
from dataclasses import dataclass
from .state import DialogueAct


class AmbiguityType(Enum):
    """Types of ambiguity that can be detected."""
    ENTITY_AMBIGUITY = "entity_ambiguity"  # Unclear what specific entity is being referenced
    SCOPE_AMBIGUITY = "scope_ambiguity"    # Unclear scope or context of the request
    INTENT_AMBIGUITY = "intent_ambiguity"  # Unclear what the user wants to do
    TEMPORAL_AMBIGUITY = "temporal_ambiguity"  # Unclear timing or date references
    QUANTIFIER_AMBIGUITY = "quantifier_ambiguity"  # Unclear quantities or amounts
    REFERENCE_AMBIGUITY = "reference_ambiguity"  # Unclear pronoun or reference resolution
    CONTEXT_AMBIGUITY = "context_ambiguity"  # Missing context for proper understanding


@dataclass
class AmbiguityDetection:
    """Represents a detected ambiguity in user input."""
    type: AmbiguityType
    confidence: float  # 0.0 to 1.0
    description: str
    position: Tuple[int, int]  # Start and end positions in the text
    suggested_clarification: str


class AmbiguityDetector:
    """Detects ambiguities in user requests."""
    
    def __init__(self):
        """Initialize the ambiguity detector."""
        # Patterns for detecting different types of ambiguity
        self.patterns = {
            AmbiguityType.ENTITY_AMBIGUITY: [
                r'\b(it|this|that|these|those)\b',
                r'\b(he|she|they|them|we|us)\b',
                r'\b(the thing|the stuff|this one|that one)\b'
            ],
            AmbiguityType.SCOPE_AMBIGUITY: [
                r'\b(all|everything|everywhere)\b',
                r'\b(some|a few|several)\b.*\b(of (them|it|this))\b',
                r'\b(part of|some of|a bit of)\b',
                r'\b(a few of those things)\b'
            ],
            AmbiguityType.INTENT_AMBIGUITY: [
                r'\b(help me|can you|could you|would you)\b.*\?$',
                r'\b(i need|i want)\b.*\?$',
                r'\b(what about|how about)\b',
                r'\b(i need help with this)\b'
            ],
            AmbiguityType.TEMPORAL_AMBIGUITY: [
                r'\b(sometimes|often|usually|occasionally)\b',
                r'\b(later|soon|in a bit|in a moment)\b',
                r'\b(when|whenever|while)\b.*\?',
                r'\b(recently|lately|before|afterwards)\b'
            ],
            AmbiguityType.QUANTIFIER_AMBIGUITY: [
                r'\b(a lot of|a bunch of|a lot|many|much)\b',
                r'\b(few|a few|several|some)\b',
                r'\b(enough|too much|too many)\b'
            ],
            AmbiguityType.REFERENCE_AMBIGUITY: [
                r'\b(this|that|these|those)\b.*\?',
                r'\b(he|she|it|they|them)\b.*\?',
                r'\b(one|ones)\b.*\b(refer to|mean|talking about)\b'
            ],
            AmbiguityType.CONTEXT_AMBIGUITY: [
                r'\b(in that case|given that|considering that)\b',
                r'\b(as we discussed|as mentioned|like before)\b',
                r'\b(based on|according to)\b.*\b(you|your|previous)\b'
            ]
        }
        
        # Keywords that might indicate ambiguity
        self.ambiguity_indicators = {
            "vague_terms": ["thing", "stuff", "something", "someone", "somewhere", "somehow"],
            "incomplete_phrases": ["i want", "i need", "help me", "can you", "could you"],
            "comparative_terms": ["better", "worse", "more", "less", "faster", "slower"],
            "conditional_terms": ["if", "unless", "whether", "in case"]
        }
    
    def detect_ambiguities(self, text: str) -> List[AmbiguityDetection]:
        """
        Detect ambiguities in the given text.
        
        Args:
            text (str): User input text to analyze
            
        Returns:
            List[AmbiguityDetection]: List of detected ambiguities
        """
        text_lower = text.lower().strip()
        ambiguities = []
        
        # Check for pattern-based ambiguities
        for ambiguity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    ambiguity = self._create_ambiguity_detection(
                        ambiguity_type, 
                        match, 
                        text, 
                        text_lower
                    )
                    ambiguities.append(ambiguity)
        
        # Check for keyword-based ambiguities
        keyword_ambiguities = self._detect_keyword_ambiguities(text_lower)
        ambiguities.extend(keyword_ambiguities)
        
        # Check for dialogue act-based ambiguities
        dialogue_ambiguity = self._detect_dialogue_act_ambiguity(text)
        if dialogue_ambiguity:
            ambiguities.append(dialogue_ambiguity)
        
        # Remove duplicates and sort by confidence
        unique_ambiguities = self._remove_duplicates(ambiguities)
        unique_ambiguities.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_ambiguities
    
    def _create_ambiguity_detection(self, ambiguity_type: AmbiguityType, 
                                  match, text: str, text_lower: str) -> AmbiguityDetection:
        """
        Create an AmbiguityDetection object based on a pattern match.
        
        Args:
            ambiguity_type (AmbiguityType): Type of ambiguity detected
            match: Regex match object
            text (str): Original text
            text_lower (str): Lowercase version of text
            
        Returns:
            AmbiguityDetection: Created ambiguity detection object
        """
        start, end = match.span()
        matched_text = text[start:end]
        
        # Calculate confidence based on match characteristics
        confidence = self._calculate_confidence(ambiguity_type, matched_text, text_lower)
        
        # Generate description and suggested clarification
        description, clarification = self._generate_description_and_clarification(
            ambiguity_type, matched_text
        )
        
        return AmbiguityDetection(
            type=ambiguity_type,
            confidence=confidence,
            description=description,
            position=(start, end),
            suggested_clarification=clarification
        )
    
    def _calculate_confidence(self, ambiguity_type: AmbiguityType, 
                            matched_text: str, text_lower: str) -> float:
        """
        Calculate confidence score for an ambiguity detection.
        
        Args:
            ambiguity_type (AmbiguityType): Type of ambiguity
            matched_text (str): Text that matched the pattern
            text_lower (str): Lowercase version of the full text
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Base confidence based on ambiguity type
        base_confidence = {
            AmbiguityType.ENTITY_AMBIGUITY: 0.7,
            AmbiguityType.SCOPE_AMBIGUITY: 0.6,
            AmbiguityType.INTENT_AMBIGUITY: 0.8,
            AmbiguityType.TEMPORAL_AMBIGUITY: 0.6,
            AmbiguityType.QUANTIFIER_AMBIGUITY: 0.5,
            AmbiguityType.REFERENCE_AMBIGUITY: 0.7,
            AmbiguityType.CONTEXT_AMBIGUITY: 0.6
        }.get(ambiguity_type, 0.5)
        
        # Adjust based on context
        adjustment = 0.0
        
        # Increase confidence if the ambiguous phrase is at the end of a question
        if text_lower.endswith(matched_text) and '?' in text_lower:
            adjustment += 0.1
        
        # Decrease confidence if the text is very short (likely less context)
        if len(text_lower) < 10:
            adjustment -= 0.2
        
        confidence = base_confidence + adjustment
        return max(0.0, min(1.0, confidence))  # Clamp between 0.0 and 1.0
    
    def _generate_description_and_clarification(self, ambiguity_type: AmbiguityType, 
                                              matched_text: str) -> Tuple[str, str]:
        """
        Generate description and suggested clarification for an ambiguity.
        
        Args:
            ambiguity_type (AmbiguityType): Type of ambiguity
            matched_text (str): Text that was matched
            
        Returns:
            Tuple[str, str]: Description and suggested clarification
        """
        descriptions = {
            AmbiguityType.ENTITY_AMBIGUITY: f"Unclear reference to '{matched_text}'",
            AmbiguityType.SCOPE_AMBIGUITY: f"Unclear scope with '{matched_text}'",
            AmbiguityType.INTENT_AMBIGUITY: f"Unclear intent with '{matched_text}'",
            AmbiguityType.TEMPORAL_AMBIGUITY: f"Unclear timing with '{matched_text}'",
            AmbiguityType.QUANTIFIER_AMBIGUITY: f"Unclear quantity with '{matched_text}'",
            AmbiguityType.REFERENCE_AMBIGUITY: f"Unclear reference to '{matched_text}'",
            AmbiguityType.CONTEXT_AMBIGUITY: f"Missing context with '{matched_text}'"
        }
        
        clarifications = {
            AmbiguityType.ENTITY_AMBIGUITY: "Could you be more specific about what you're referring to?",
            AmbiguityType.SCOPE_AMBIGUITY: "Could you clarify what you mean by that?",
            AmbiguityType.INTENT_AMBIGUITY: "What exactly would you like me to help you with?",
            AmbiguityType.TEMPORAL_AMBIGUITY: "When are you referring to?",
            AmbiguityType.QUANTIFIER_AMBIGUITY: "How much or how many are you referring to?",
            AmbiguityType.REFERENCE_AMBIGUITY: "What specifically are you referring to?",
            AmbiguityType.CONTEXT_AMBIGUITY: "Could you provide more context for your request?"
        }
        
        description = descriptions.get(ambiguity_type, f"Ambiguity detected with '{matched_text}'")
        clarification = clarifications.get(ambiguity_type, "Could you clarify what you mean?")
        
        return description, clarification
    
    def _detect_keyword_ambiguities(self, text_lower: str) -> List[AmbiguityDetection]:
        """
        Detect ambiguities based on keywords.
        
        Args:
            text_lower (str): Lowercase version of text to analyze
            
        Returns:
            List[AmbiguityDetection]: List of detected ambiguities
        """
        ambiguities = []
        
        # Check for vague terms
        for term in self.ambiguity_indicators["vague_terms"]:
            if term in text_lower:
                start = text_lower.find(term)
                end = start + len(term)
                ambiguities.append(AmbiguityDetection(
                    type=AmbiguityType.ENTITY_AMBIGUITY,
                    confidence=0.6,
                    description=f"Vague term '{term}' used",
                    position=(start, end),
                    suggested_clarification="Could you be more specific about what you mean?"
                ))
        
        # Check for incomplete phrases at the end of sentences
        for phrase in self.ambiguity_indicators["incomplete_phrases"]:
            if text_lower.endswith(phrase):
                start = text_lower.find(phrase)
                end = start + len(phrase)
                ambiguities.append(AmbiguityDetection(
                    type=AmbiguityType.INTENT_AMBIGUITY,
                    confidence=0.8,
                    description=f"Incomplete request ending with '{phrase}'",
                    position=(start, end),
                    suggested_clarification="What specifically would you like me to do?"
                ))
        
        return ambiguities
    
    def _detect_dialogue_act_ambiguity(self, text: str) -> Optional[AmbiguityDetection]:
        """
        Detect ambiguity based on dialogue act patterns.
        
        Args:
            text (str): User input text
            
        Returns:
            Optional[AmbiguityDetection]: Detected ambiguity or None
        """
        text_lower = text.lower().strip()
        
        # Check for questions that might be ambiguous
        if text_lower.endswith('?'):
            # Questions with vague terms
            vague_question_indicators = ["what", "how", "which"]
            if any(indicator in text_lower for indicator in vague_question_indicators):
                # Check if the question lacks specific details
                specific_terms = ["name", "date", "time", "place", "number", "amount"]
                if not any(term in text_lower for term in specific_terms):
                    return AmbiguityDetection(
                        type=AmbiguityType.INTENT_AMBIGUITY,
                        confidence=0.7,
                        description="General question without specific details",
                        position=(0, len(text)),
                        suggested_clarification="Could you be more specific about what information you're looking for?"
                    )
        
        return None
    
    def _remove_duplicates(self, ambiguities: List[AmbiguityDetection]) -> List[AmbiguityDetection]:
        """
        Remove duplicate ambiguity detections.
        
        Args:
            ambiguities (List[AmbiguityDetection]): List of ambiguities
            
        Returns:
            List[AmbiguityDetection]: List with duplicates removed
        """
        unique_ambiguities = []
        seen_positions = set()
        
        for ambiguity in ambiguities:
            pos_key = (ambiguity.position[0], ambiguity.position[1], ambiguity.type.value)
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_ambiguities.append(ambiguity)
        
        return unique_ambiguities
    
    def get_highest_confidence_ambiguity(self, text: str) -> Optional[AmbiguityDetection]:
        """
        Get the highest confidence ambiguity detection for the given text.
        
        Args:
            text (str): User input text
            
        Returns:
            Optional[AmbiguityDetection]: Highest confidence ambiguity or None
        """
        ambiguities = self.detect_ambiguities(text)
        if ambiguities:
            return max(ambiguities, key=lambda x: x.confidence)
        return None
    
    def has_ambiguity(self, text: str, min_confidence: float = 0.5) -> bool:
        """
        Check if the text contains any ambiguities above the minimum confidence threshold.
        
        Args:
            text (str): User input text
            min_confidence (float): Minimum confidence threshold (default: 0.5)
            
        Returns:
            bool: True if ambiguity is detected, False otherwise
        """
        ambiguities = self.detect_ambiguities(text)
        return any(ambiguity.confidence >= min_confidence for ambiguity in ambiguities)


# Pre-instantiated detector for convenience
ambiguity_detector = AmbiguityDetector()