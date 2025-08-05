"""
Question Generator for Personal Agent

This module provides functionality for generating follow-up questions to clarify ambiguous user requests.
"""

from typing import List, Dict, Optional, Tuple
from .ambiguity_detector import AmbiguityDetection, AmbiguityType
from .state import DialogueAct
import random


class QuestionGenerator:
    """Generates follow-up questions to clarify ambiguous user requests."""
    
    def __init__(self):
        """Initialize the question generator."""
        # Templates for different types of ambiguities
        self.question_templates = {
            AmbiguityType.ENTITY_AMBIGUITY: [
                "Could you be more specific about what you're referring to?",
                "What exactly are you talking about?",
                "Can you clarify what you mean by that?",
                "Which specific {entity} are you referring to?",
                "I'm not sure what you mean. Could you provide more details?"
            ],
            AmbiguityType.SCOPE_AMBIGUITY: [
                "Could you clarify what you mean by that?",
                "What specifically are you referring to?",
                "Can you be more specific about the scope?",
                "Are you referring to all of them or just some?",
                "What exactly do you mean by '{scope}'?"
            ],
            AmbiguityType.INTENT_AMBIGUITY: [
                "What exactly would you like me to help you with?",
                "Could you clarify what you're trying to accomplish?",
                "What specifically are you looking for?",
                "Can you tell me more about what you need?",
                "I'd like to help, but I'm not sure what you want. Could you explain?"
            ],
            AmbiguityType.TEMPORAL_AMBIGUITY: [
                "When are you referring to?",
                "Could you be more specific about the timing?",
                "What time period are you asking about?",
                "Are you referring to now, in the past, or in the future?",
                "Can you clarify when you mean?"
            ],
            AmbiguityType.QUANTIFIER_AMBIGUITY: [
                "How much or how many are you referring to?",
                "Could you be more specific about the quantity?",
                "What amount are you asking about?",
                "Can you give me a specific number?",
                "How many exactly?"
            ],
            AmbiguityType.REFERENCE_AMBIGUITY: [
                "What specifically are you referring to?",
                "Could you clarify what you mean by that?",
                "Which one are you talking about?",
                "I'm not sure what you're referring to. Could you be more specific?",
                "Can you tell me more about what you mean?"
            ],
            AmbiguityType.CONTEXT_AMBIGUITY: [
                "Could you provide more context for your request?",
                "Can you give me more background information?",
                "I'm not sure I understand the context. Could you explain more?",
                "What situation are you referring to?",
                "Could you clarify the circumstances you're asking about?"
            ]
        }
        
        # Fallback templates for general clarification
        self.fallback_templates = [
            "Could you clarify what you mean?",
            "I'm not sure I understand. Could you explain more?",
            "Can you be more specific about what you're asking?",
            "Could you provide more details?",
            "I'd like to help, but I need a bit more information. What exactly do you mean?"
        ]
        
        # Context-aware templates that consider previous conversation
        self.contextual_templates = {
            "default": [
                "To better assist you, could you clarify: {question}",
                "I want to make sure I understand correctly. {question}",
                "Could you help me understand what you mean by that? {question}",
                "To provide the best response, I need a bit more information: {question}",
                "Could you elaborate on that point? {question}"
            ]
        }
    
    def generate_clarification_question(self, ambiguity: AmbiguityDetection, 
                                      context: Optional[Dict] = None) -> str:
        """
        Generate a clarification question for a detected ambiguity.
        
        Args:
            ambiguity (AmbiguityDetection): Detected ambiguity
            context (Optional[Dict]): Conversation context
            
        Returns:
            str: Generated clarification question
        """
        # Get templates for the ambiguity type
        templates = self.question_templates.get(ambiguity.type, self.fallback_templates)
        
        # Select a template
        template = random.choice(templates)
        
        # Customize the template based on the ambiguity
        question = self._customize_template(template, ambiguity)
        
        # Add context if available
        if context:
            question = self._add_context_to_question(question, context)
        
        return question
    
    def generate_multiple_questions(self, ambiguities: List[AmbiguityDetection], 
                                  max_questions: int = 3,
                                  context: Optional[Dict] = None) -> List[str]:
        """
        Generate multiple clarification questions for a list of ambiguities.
        
        Args:
            ambiguities (List[AmbiguityDetection]): List of detected ambiguities
            max_questions (int): Maximum number of questions to generate (default: 3)
            context (Optional[Dict]): Conversation context
            
        Returns:
            List[str]: List of generated clarification questions
        """
        # Sort ambiguities by confidence
        sorted_ambiguities = sorted(ambiguities, key=lambda x: x.confidence, reverse=True)
        
        # Limit to max_questions
        top_ambiguities = sorted_ambiguities[:max_questions]
        
        # Generate questions
        questions = []
        for ambiguity in top_ambiguities:
            question = self.generate_clarification_question(ambiguity, context)
            questions.append(question)
        
        return questions
    
    def generate_contextual_question(self, user_input: str, 
                                   dialogue_act: DialogueAct,
                                   context: Optional[Dict] = None) -> str:
        """
        Generate a contextual question based on user input and dialogue act.
        
        Args:
            user_input (str): User input text
            dialogue_act (DialogueAct): Recognized dialogue act
            context (Optional[Dict]): Conversation context
            
        Returns:
            str: Generated contextual question
        """
        # Get appropriate template based on dialogue act
        if dialogue_act == DialogueAct.QUESTION:
            templates = [
                "Could you tell me more about your question?",
                "What specifically would you like to know about that?",
                "I'd be happy to help with your question. Could you provide more details?"
            ]
        elif dialogue_act == DialogueAct.REQUEST:
            templates = [
                "What specifically would you like me to do?",
                "Could you tell me more about what you need?",
                "I'm here to help. What exactly are you looking for?"
            ]
        elif dialogue_act == DialogueAct.CLARIFICATION:
            templates = [
                "I see you're asking for clarification. What specifically would you like me to explain?",
                "Could you tell me what part you'd like me to clarify?",
                "What would you like me to explain in more detail?"
            ]
        else:
            templates = self.fallback_templates
        
        # Select a template
        template = random.choice(templates)
        
        # Add context if available
        if context:
            template = self._add_context_to_question(template, context)
        
        return template
    
    def _customize_template(self, template: str, ambiguity: AmbiguityDetection) -> str:
        """
        Customize a template based on the ambiguity details.
        
        Args:
            template (str): Question template
            ambiguity (AmbiguityDetection): Detected ambiguity
            
        Returns:
            str: Customized question
        """
        # Extract the ambiguous text
        # For now, we'll just return the template as is
        # In a more advanced implementation, we could customize based on the specific text
        return template
    
    def _add_context_to_question(self, question: str, context: Dict) -> str:
        """
        Add context to a question to make it more relevant.
        
        Args:
            question (str): Base question
            context (Dict): Conversation context
            
        Returns:
            str: Contextualized question
        """
        # Get contextual templates
        contextual_templates = self.contextual_templates.get("default", ["{question}"])
        
        # Select a contextual template
        contextual_template = random.choice(contextual_templates)
        
        # Apply the template
        contextualized_question = contextual_template.replace("{question}", question)
        
        return contextualized_question
    
    def generate_adaptive_question(self, ambiguity: AmbiguityDetection, 
                                 user_preferences: Optional[List[str]] = None,
                                 conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate an adaptive question based on user preferences and conversation history.
        
        Args:
            ambiguity (AmbiguityDetection): Detected ambiguity
            user_preferences (Optional[List[str]]): User preferences
            conversation_history (Optional[List[Dict]]): Conversation history
            
        Returns:
            str: Adaptive clarification question
        """
        # Start with a basic question
        question = self.generate_clarification_question(ambiguity)
        
        # Adapt based on user preferences if available
        if user_preferences:
            # For example, if user prefers direct communication, make question more direct
            if any(pref.lower() in ["direct", "concise", "straightforward"] for pref in user_preferences):
                question = self._make_question_more_direct(question)
        
        # Adapt based on conversation history if available
        if conversation_history and len(conversation_history) > 2:
            # Check if we've asked similar questions recently
            recent_questions = [
                turn["content"] for turn in conversation_history[-4:] 
                if turn["role"] == "assistant" and "?" in turn["content"]
            ]
            
            if recent_questions and self._is_similar_question(question, recent_questions):
                # Rephrase to avoid repetition
                question = self._rephrase_question(question)
        
        return question
    
    def _make_question_more_direct(self, question: str) -> str:
        """
        Make a question more direct and concise.
        
        Args:
            question (str): Original question
            
        Returns:
            str: More direct question
        """
        # Remove polite prefixes
        direct_forms = {
            "Could you be more specific about what you're referring to?": "What are you referring to?",
            "Could you clarify what you mean by that?": "What do you mean?",
            "What exactly would you like me to help you with?": "What do you want?",
            "How much or how many are you referring to?": "How many?",
            "When are you referring to?": "When?",
            "What specifically are you referring to?": "What do you mean?",
            "Could you provide more context for your request?": "More context?",
            "Could you clarify what you're trying to accomplish?": "What are you trying to do?"
        }
        
        return direct_forms.get(question, question)
    
    def _is_similar_question(self, question: str, recent_questions: List[str]) -> bool:
        """
        Check if a question is similar to recent questions.
        
        Args:
            question (str): Question to check
            recent_questions (List[str]): Recent questions
            
        Returns:
            bool: True if similar, False otherwise
        """
        # Simple similarity check based on keywords
        question_keywords = set(question.lower().split())
        
        for recent_q in recent_questions:
            recent_keywords = set(recent_q.lower().split())
            # If more than 50% of keywords overlap, consider them similar
            if len(question_keywords.intersection(recent_keywords)) > len(question_keywords) * 0.5:
                return True
        
        return False
    
    def _rephrase_question(self, question: str) -> str:
        """
        Rephrase a question to avoid repetition.
        
        Args:
            question (str): Question to rephrase
            
        Returns:
            str: Rephrased question
        """
        rephrased_forms = {
            "Could you be more specific about what you're referring to?": "Can you tell me exactly what you mean?",
            "What exactly would you like me to help you with?": "What kind of help are you looking for?",
            "Could you clarify what you mean by that?": "Can you explain that differently?",
            "How much or how many are you referring to?": "What quantity are you asking about?",
            "When are you referring to?": "What time are you asking about?",
            "What specifically are you referring to?": "Which one do you mean?",
            "Could you provide more context for your request?": "Can you give me more background?",
            "Could you clarify what you're trying to accomplish?": "What's your goal here?"
        }
        
        return rephrased_forms.get(question, f"Let me ask differently: {question}")


# Pre-instantiated generator for convenience
question_generator = QuestionGenerator()