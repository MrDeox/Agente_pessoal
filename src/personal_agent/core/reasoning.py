"""
Reasoning Module for Personal Agent

This module contains functionality for advanced reasoning and decision-making.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from ..llm.client import LLMClient
from ..llm.models import Message
from ..config.settings import Config
from ..utils.logging import get_logger


class ReasoningType(Enum):
    """Enumeration of reasoning types."""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


@dataclass
class DecisionOption:
    """Represents a decision option with its attributes."""
    id: str
    description: str
    confidence: float = 0.0
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionContext:
    """Context for making a decision."""
    problem: str
    options: List[DecisionOption]
    constraints: List[str] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)
    context_info: Dict[str, Any] = field(default_factory=dict)


class ReasoningEngine:
    """Engine for advanced reasoning and decision-making."""

    def __init__(self, config: Config = None, llm_client: LLMClient = None):
        """
        Initialize the reasoning engine.
        
        Args:
            config (Config): Configuration object
            llm_client (LLMClient): LLM client instance
        """
        self.config = config or Config.load()
        self.llm_client = llm_client or LLMClient(self.config)
        self.logger = get_logger()

    def make_decision(self, context: DecisionContext) -> DecisionOption:
        """
        Make a decision based on the provided context.
        
        Args:
            context (DecisionContext): The decision context
            
        Returns:
            DecisionOption: The selected decision option
        """
        # If we have a valid LLM client, use it to make the decision
        if self.llm_client:
            try:
                return self._llm_based_decision(context)
            except Exception as e:
                self.logger.warning(f"LLM-based decision failed: {e}")
        
        # Fallback to a simple rule-based decision
        return self._rule_based_decision(context)

    def _llm_based_decision(self, context: DecisionContext) -> DecisionOption:
        """
        Make a decision using the LLM.
        
        Args:
            context (DecisionContext): The decision context
            
        Returns:
            DecisionOption: The selected decision option
        """
        # Prepare the prompt for the LLM
        prompt = self._create_decision_prompt(context)
        
        # Create messages for the LLM
        messages = [
            Message(
                role="system",
                content="You are an expert decision-making assistant. Analyze the options and select the best one based on the provided context."
            ),
            Message(
                role="user",
                content=prompt
            )
        ]
        
        # Get response from LLM
        response = self.llm_client.generate_response(messages)
        
        # Parse the response to extract the decision
        return self._parse_decision_response(response.content, context.options)

    def _create_decision_prompt(self, context: DecisionContext) -> str:
        """
        Create a prompt for the LLM to make a decision.
        
        Args:
            context (DecisionContext): The decision context
            
        Returns:
            str: The formatted prompt
        """
        prompt = f"Problem: {context.problem}\n\n"
        
        prompt += "Options:\n"
        for i, option in enumerate(context.options, 1):
            prompt += f"{i}. {option.description}\n"
            if option.pros:
                prompt += f"   Pros: {', '.join(option.pros)}\n"
            if option.cons:
                prompt += f"   Cons: {', '.join(option.cons)}\n"
        
        if context.constraints:
            prompt += f"\nConstraints: {', '.join(context.constraints)}\n"
        
        if context.preferences:
            prompt += f"\nPreferences: {', '.join(context.preferences)}\n"
        
        prompt += "\nPlease analyze the options and select the best one. Respond with only the number of the selected option."
        
        return prompt

    def _parse_decision_response(self, response: str, options: List[DecisionOption]) -> DecisionOption:
        """
        Parse the LLM response to extract the decision.
        
        Args:
            response (str): The LLM response
            options (List[DecisionOption]): The available options
            
        Returns:
            DecisionOption: The selected decision option
        """
        # Try to extract a number from the response
        try:
            # Look for a number in the response
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                selected_index = int(numbers[0]) - 1  # Convert to 0-based index
                if 0 <= selected_index < len(options):
                    return options[selected_index]
        except Exception as e:
            self.logger.warning(f"Error parsing decision response: {e}")
        
        # Fallback to the first option if parsing fails
        return options[0] if options else None

    def _rule_based_decision(self, context: DecisionContext) -> DecisionOption:
        """
        Make a decision using a simple rule-based approach.
        
        Args:
            context (DecisionContext): The decision context
            
        Returns:
            DecisionOption: The selected decision option
        """
        # Simple rule: select the option with the highest confidence
        if context.options:
            return max(context.options, key=lambda x: x.confidence)
        return None

    def reason(self, premises: List[str], reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE) -> str:
        """
        Perform logical reasoning based on premises.
        
        Args:
            premises (List[str]): The premises to reason from
            reasoning_type (ReasoningType): The type of reasoning to use
            
        Returns:
            str: The conclusion
        """
        # If we have a valid LLM client, use it for reasoning
        if self.llm_client:
            try:
                return self._llm_based_reasoning(premises, reasoning_type)
            except Exception as e:
                self.logger.warning(f"LLM-based reasoning failed: {e}")
        
        # Fallback to a simple rule-based reasoning
        return self._rule_based_reasoning(premises, reasoning_type)

    def _llm_based_reasoning(self, premises: List[str], reasoning_type: ReasoningType) -> str:
        """
        Perform reasoning using the LLM.
        
        Args:
            premises (List[str]): The premises to reason from
            reasoning_type (ReasoningType): The type of reasoning to use
            
        Returns:
            str: The conclusion
        """
        # Prepare the prompt for the LLM
        prompt = self._create_reasoning_prompt(premises, reasoning_type)
        
        # Create messages for the LLM
        messages = [
            Message(
                role="system",
                content="You are an expert logical reasoning assistant. Analyze the premises and provide a logical conclusion."
            ),
            Message(
                role="user",
                content=prompt
            )
        ]
        
        # Get response from LLM
        response = self.llm_client.generate_response(messages)
        return response.content

    def _create_reasoning_prompt(self, premises: List[str], reasoning_type: ReasoningType) -> str:
        """
        Create a prompt for the LLM to perform reasoning.
        
        Args:
            premises (List[str]): The premises to reason from
            reasoning_type (ReasoningType): The type of reasoning to use
            
        Returns:
            str: The formatted prompt
        """
        prompt = f"Perform {reasoning_type.value} reasoning on the following premises:\n\n"
        for i, premise in enumerate(premises, 1):
            prompt += f"{i}. {premise}\n"
        
        prompt += "\nProvide a logical conclusion based on these premises."
        return prompt

    def _rule_based_reasoning(self, premises: List[str], reasoning_type: ReasoningType) -> str:
        """
        Perform reasoning using a simple rule-based approach.
        
        Args:
            premises (List[str]): The premises to reason from
            reasoning_type (ReasoningType): The type of reasoning to use
            
        Returns:
            str: The conclusion
        """
        # Simple rule-based reasoning
        if not premises:
            return "No premises provided, cannot draw conclusion."
        
        if reasoning_type == ReasoningType.DEDUCTIVE:
            return f"Based on the premises: {', '.join(premises)}, a logical conclusion can be drawn."
        elif reasoning_type == ReasoningType.INDUCTIVE:
            return f"From the premises: {', '.join(premises)}, we can induce a general principle."
        elif reasoning_type == ReasoningType.ABDUCTIVE:
            return f"Given the premises: {', '.join(premises)}, the most likely explanation is..."
        else:  # ANALOGICAL
            return f"By analogy with: {', '.join(premises)}, we can conclude..."

    def evaluate_options(self, options: List[DecisionOption], criteria: List[str]) -> List[DecisionOption]:
        """
        Evaluate options based on specific criteria.
        
        Args:
            options (List[DecisionOption]): The options to evaluate
            criteria (List[str]): The criteria to evaluate against
            
        Returns:
            List[DecisionOption]: The evaluated options, sorted by score
        """
        # If we have a valid LLM client, use it for evaluation
        if self.llm_client:
            try:
                return self._llm_based_evaluation(options, criteria)
            except Exception as e:
                self.logger.warning(f"LLM-based evaluation failed: {e}")
        
        # Fallback to a simple rule-based evaluation
        return self._rule_based_evaluation(options, criteria)

    def _llm_based_evaluation(self, options: List[DecisionOption], criteria: List[str]) -> List[DecisionOption]:
        """
        Evaluate options using the LLM.
        
        Args:
            options (List[DecisionOption]): The options to evaluate
            criteria (List[str]): The criteria to evaluate against
            
        Returns:
            List[DecisionOption]: The evaluated options, sorted by score
        """
        # Prepare the prompt for the LLM
        prompt = self._create_evaluation_prompt(options, criteria)
        
        # Create messages for the LLM
        messages = [
            Message(
                role="system",
                content="You are an expert evaluation assistant. Evaluate the options based on the provided criteria and assign confidence scores."
            ),
            Message(
                role="user",
                content=prompt
            )
        ]
        
        # Get response from LLM
        response = self.llm_client.generate_response(messages)
        
        # Parse the response to update option scores
        updated_options = self._parse_evaluation_response(response.content, options)
        return sorted(updated_options, key=lambda x: x.confidence, reverse=True)

    def _create_evaluation_prompt(self, options: List[DecisionOption], criteria: List[str]) -> str:
        """
        Create a prompt for the LLM to evaluate options.
        
        Args:
            options (List[DecisionOption]): The options to evaluate
            criteria (List[str]): The criteria to evaluate against
            
        Returns:
            str: The formatted prompt
        """
        prompt = "Evaluate the following options based on these criteria:\n\n"
        prompt += f"Criteria: {', '.join(criteria)}\n\n"
        
        prompt += "Options:\n"
        for i, option in enumerate(options, 1):
            prompt += f"{i}. {option.description}\n"
            if option.pros:
                prompt += f"   Pros: {', '.join(option.pros)}\n"
            if option.cons:
                prompt += f"   Cons: {', '.join(option.cons)}\n"
        
        prompt += "\nFor each option, provide a confidence score (0-100) based on how well it meets the criteria. Respond in JSON format with the scores."
        return prompt

    def _parse_evaluation_response(self, response: str, options: List[DecisionOption]) -> List[DecisionOption]:
        """
        Parse the LLM response to extract evaluation scores.
        
        Args:
            response (str): The LLM response
            options (List[DecisionOption]): The options to update
            
        Returns:
            List[DecisionOption]: The updated options
        """
        try:
            # Try to parse as JSON
            scores_data = json.loads(response)
            if isinstance(scores_data, dict) and "scores" in scores_data:
                scores = scores_data["scores"]
                for i, option in enumerate(options):
                    if i < len(scores):
                        option.confidence = float(scores[i])
            return options
        except Exception as e:
            self.logger.warning(f"Error parsing evaluation response: {e}")
            return options

    def _rule_based_evaluation(self, options: List[DecisionOption], criteria: List[str]) -> List[DecisionOption]:
        """
        Evaluate options using a simple rule-based approach.
        
        Args:
            options (List[DecisionOption]): The options to evaluate
            criteria (List[str]): The criteria to evaluate against
            
        Returns:
            List[DecisionOption]: The evaluated options, sorted by score
        """
        # Simple rule: return options sorted by existing confidence
        return sorted(options, key=lambda x: x.confidence, reverse=True)