"""
Agent Module for Personal Agent

This module contains the core Agent class that orchestrates the personal agent's functionality.
"""

from typing import List
from ..memory.storage import SQLiteMemoryStorage, MemoryStorage
from ..memory.models import MemoryItem
from ..config.settings import Config
from ..llm.client import LLMClient
from ..llm.models import Message
from ..llm.exceptions import LLMException
from .error_recovery import error_recovery_manager
from .feedback import FeedbackSystem
from ..utils.validation import validate_message_content, ValidationError
from ..utils.logging import get_logger, log_exception
from ..utils.common import generate_id, find_conversation_id
from .planning import PlanningEngine, Task
from .reasoning import ReasoningEngine, DecisionContext, DecisionOption, ReasoningType
from .decision_trees import DecisionTreeManager, ScenarioType
from ..context.processor import ContextProcessor
from ..conversation.interface import EnhancedConversationInterface
from ..conversation.dialogue_act import dialogue_act_recognizer
from ..conversation.state import ConversationState
from .error_metrics import error_metrics_collector
from ..conversation.manager import ConversationManager
from ..core.error_handler import ErrorHandler
from ..memory.service import MemoryService
from ..llm.service import LLMService
from ..core.response_processor import ResponseProcessor
from ..core.request_classifier import RequestClassifier

class Agent:
    """
    Main orchestrator of the personal agent's functionality.
    """
    
    def __init__(self, user_id: str = "default_user", config: Config = None,
                 memory_storage: MemoryStorage = None, llm_client: LLMClient = None,
                 feedback_system: FeedbackSystem = None):
        """
        Initialize the agent.
        
        Args:
            user_id (str): ID of the user interacting with the agent
            config (Config): Configuration object. If None, will load default config.
            memory_storage (MemoryStorage): Memory storage instance. If None, will create default.
            llm_client (LLMClient): LLM client instance. If None, will create default.
            feedback_system (FeedbackSystem): Feedback system instance. If None, will create default.
        """
        self.name = "Personal Agent"
        self.version = "0.1.0"
        self.user_id = user_id
        
        # Initialize configuration
        self.config = config or Config.load()
        
        # Initialize core services
        self.conversation_manager = ConversationManager(user_id=user_id, memory_storage=memory_storage)
        self.error_handler = ErrorHandler()
        self.memory_service = MemoryService(config=self.config, memory_storage=memory_storage)
        self.llm_service = LLMService(config=self.config, llm_client=llm_client)
        self.response_processor = ResponseProcessor(user_id=user_id, feedback_system=feedback_system)
        self.request_classifier = RequestClassifier()
        
        # Initialize planning engine
        self.planning_engine = PlanningEngine()
        
        # Initialize reasoning engine
        self.reasoning_engine = ReasoningEngine(config=self.config, llm_client=llm_client)
        
        # Initialize decision tree manager
        self.decision_tree_manager = DecisionTreeManager()
        
        # Initialize context processor
        self.context_processor = ContextProcessor()
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input (str): The input from the user
            
        Returns:
            str: The agent's response
        """
        # Validate user input
        try:
            validated_input = validate_message_content(user_input)
        except ValidationError as e:
            logger = get_logger()
            logger.warning(f"Input validation error: {e}")
            return "I'm sorry, but your input contains invalid characters. Please try again."
        
        # Store user input in conversation history using conversation manager
        self.conversation_manager.add_user_message(validated_input)
        
        # Check for exit commands
        if self.conversation_manager.is_exit_command(validated_input):
            response = "Goodbye! Have a great day!"
            response_id = None
        else:
            # Check if we're currently asking for clarification
            if self.conversation_manager.get_state() == ConversationState.ASKING_CLARIFICATION:
                # We're in a clarification loop, process the response as clarification
                response = self._handle_clarification_response(validated_input)
            else:
                # Normal processing flow
                # Check for planning requests
                if self.request_classifier.is_planning_request(validated_input):
                    raw_response = self._handle_planning_request(validated_input)
                    # Enhance the response using the response processor
                    response = self.response_processor.enhance_response(validated_input, raw_response)
                # Check for reasoning requests
                elif self.request_classifier.is_reasoning_request(validated_input):
                    raw_response = self._handle_reasoning_request(validated_input)
                    # Enhance the response using the response processor
                    response = self.response_processor.enhance_response(validated_input, raw_response)
                # Check for decision tree requests
                elif self.request_classifier.is_decision_tree_request(validated_input):
                    raw_response = self._handle_decision_tree_request(validated_input)
                    # Enhance the response using the response processor
                    response = self.response_processor.enhance_response(validated_input, raw_response)
                else:
                    # Try to generate a response using LLM
                    try:
                        # Get memory context using memory service
                        memory_context = self.memory_service.get_memory_context(
                            self.user_id,
                            self.conversation_manager.get_recent_history(),
                            validated_input
                        )
                        
                        # Generate response using LLM service
                        raw_response = self.llm_service.generate_response(
                            validated_input,
                            self.conversation_manager.get_recent_history(),
                            memory_context
                        )
                        
                        # Enhance the response using the response processor
                        response = self.response_processor.enhance_response(validated_input, raw_response)
                    except LLMException as e:
                        # Handle LLM exceptions using error handler
                        context = {
                            "user_input": validated_input,
                            "conversation_history": self.conversation_manager.get_recent_history()
                        }
                        response = self.error_handler.handle_llm_exception(e, context)
                    except Exception as e:
                        # Handle unexpected exceptions using error handler
                        context = {
                            "user_input": validated_input,
                            "conversation_history": self.conversation_manager.get_recent_history()
                        }
                        response = self.error_handler.handle_unexpected_exception(e, context)
                    
                    # Check if we should adapt the response based on feedback
                    recent_history = self.conversation_manager.get_recent_history()
                    if len(recent_history) >= 2:
                        # Get the previous assistant response ID if it exists
                        previous_response_id = recent_history[-2].get("id") if recent_history[-2].get("role") == "assistant" else None
                        if previous_response_id:
                            # Adapt response based on feedback using response processor
                            response = self.response_processor.adapt_response_based_on_feedback(response, previous_response_id)
        
        # Generate a unique ID for this response
        response_id = generate_id()
        
        # Store agent response in conversation history with ID using conversation manager
        self.conversation_manager.add_agent_message(response, response_id)
        
        # Save conversation turn to memory using memory service
        self.memory_service.save_conversation_turn(self.user_id, user_input, response)
        
        return response
    
    def _handle_clarification_response(self, user_input: str) -> str:
        """
        Handle user responses to clarification questions.
        
        Args:
            user_input (str): User's response to clarification questions
            
        Returns:
            str: Agent's response
        """
        # For now, we'll simply acknowledge the clarification and continue
        # In a more advanced implementation, we would use this information to better process the original request
        
        # Acknowledge the clarification
        acknowledgment = "Thank you for the clarification. "
        
        # Update the conversation state to indicate we're no longer asking for clarification
        self.conversation_manager.set_state(ConversationState.IN_PROGRESS)
        
        # Generate a response that acknowledges the clarification and continues the conversation
        response = acknowledgment + "How else can I help you?"
        
        return response

    def _handle_planning_request(self, user_input: str) -> str:
        """
        Handle a planning request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            str: The response
        """
        try:
            # Create a plan
            plan = self.create_plan(user_input)
            
            # Format the plan as a response
            response = f"I've created a plan for: {plan.description}\n\n"
            response += "Here are the steps:\n"
            
            for i, subtask in enumerate(plan.subtasks, 1):
                response += f"{i}. {subtask.description}\n"
            
            response += f"\nPlan ID: {plan.id}\n"
            response += "You can ask me to execute this plan by saying 'execute plan [ID]'"
            
            return response
        except Exception as e:
            logger = get_logger()
            logger.error(f"Error handling planning request: {e}")
            context = {
                "user_input": user_input,
                "function": "planning"
            }
            return error_recovery_manager.recover_from_error(e, context)

    def _handle_reasoning_request(self, user_input: str) -> str:
        """
        Handle a reasoning request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            str: The response
        """
        try:
            # For now, we'll do a simple reasoning task
            # In a real implementation, we would extract premises from the input
            premises = [
                "All humans are mortal",
                "Socrates is a human",
                user_input
            ]
            
            conclusion = self.reason(premises, "deductive")
            
            response = f"Based on the premises:\n"
            for premise in premises[:-1]:
                response += f"- {premise}\n"
            response += f"\nAnd your statement: {user_input}\n\n"
            response += f"The logical conclusion is: {conclusion}"
            
            return response
        except Exception as e:
            logger = get_logger()
            logger.error(f"Error handling reasoning request: {e}")
            context = {
                "user_input": user_input,
                "function": "reasoning"
            }
            return error_recovery_manager.recover_from_error(e, context)

    def _handle_decision_tree_request(self, user_input: str) -> str:
        """
        Handle a decision tree request.
        
        Args:
            user_input (str): The user input
            
        Returns:
            str: The response
        """
        try:
            # List available decision trees
            trees = self.list_decision_trees()
            
            if not trees:
                return "Sorry, no decision trees are available at the moment."
            
            # For now, we'll just use the first tree
            # In a real implementation, we would try to match the request to the appropriate tree
            tree_info = trees[0]
            tree_id = tree_info["id"]
            
            response = f"I can help you with: {tree_info['name']}\n\n"
            response += "Please answer the following questions:\n"
            
            # Get the tree to get the first question
            tree = self.decision_tree_manager.get_tree(tree_id)
            if tree and tree.root_node_id:
                root_node = tree.get_node(tree.root_node_id)
                if root_node:
                    response += f"1. {root_node.question}\n"
                    for i, option in enumerate(root_node.options, 1):
                        response += f"   {i}. {option['text']}\n"
            
            response += "\nPlease respond with the number of your choice."
            
            return response
        except Exception as e:
            logger = get_logger()
            logger.error(f"Error handling decision tree request: {e}")
            context = {
                "user_input": user_input,
                "function": "decision_tree"
            }
            return error_recovery_manager.recover_from_error(e, context)

    def get_welcome_message(self) -> str:
        """
        Generate a welcome message for new conversations.
        
        Returns:
            str: Welcome message
        """
        # Use the response processor for the welcome message
        return self.response_processor.get_welcome_message()
    
    def get_memory_context(self) -> str:
        """
        Retrieve relevant context from memory to inform responses.
        
        Returns:
            str: Formatted context from memory
        """
        # Get the last user input for relevance scoring
        last_user_input = ""
        recent_history = self.conversation_manager.get_recent_history()
        if recent_history:
            for turn in reversed(recent_history):
                if turn["role"] == "user":
                    last_user_input = turn["content"]
                    break
        
        # Delegate to memory service
        return self.memory_service.get_memory_context(self.user_id, recent_history, last_user_input)
    
    def remember_preference(self, key: str, value: str = None) -> bool:
        """
        Store a user preference in memory.
        
        Args:
            key (str): The preference key or the full preference string if value is None
            value (str): The preference value (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Handle both calling conventions:
        # 1. remember_preference("language", "English")
        # 2. remember_preference("language: English")
        if value is not None:
            preference = f"{key}: {value}"
        else:
            preference = key
            
        # Delegate to memory service
        return self.memory_service.remember_preference(self.user_id, preference)
    
    def collect_rating_feedback(self, message_id: str, rating: int, comment: str = None) -> bool:
        """
        Collect rating feedback for a specific message.
        
        Args:
            message_id (str): ID of the message being rated
            rating (int): Rating value (typically 1-5)
            comment (str): Optional comment about the feedback
            
        Returns:
            bool: True if feedback was saved successfully, False otherwise
        """
        # Get current conversation ID if available
        conversation_id = find_conversation_id(self.conversation_manager.get_recent_history(), message_id)
        
        # Delegate to response processor
        return self.response_processor.collect_rating_feedback(
            message_id=message_id,
            rating=rating,
            conversation_id=conversation_id,
            comment=comment
        )
    
    def collect_thumbs_feedback(self, message_id: str, is_positive: bool, comment: str = None) -> bool:
        """
        Collect thumbs up/down feedback for a specific message.
        
        Args:
            message_id (str): ID of the message being rated
            is_positive (bool): True for thumbs up, False for thumbs down
            comment (str): Optional comment about the feedback
            
        Returns:
            bool: True if feedback was saved successfully, False otherwise
        """
        # Get current conversation ID if available
        conversation_id = find_conversation_id(self.conversation_manager.get_recent_history(), message_id)
        
        # Delegate to response processor
        return self.response_processor.collect_thumbs_feedback(
            message_id=message_id,
            is_positive=is_positive,
            conversation_id=conversation_id,
            comment=comment
        )
    
    def get_feedback_statistics(self) -> dict:
        """
        Get feedback statistics for the current user.
        
        Returns:
            dict: Feedback statistics
        """
        # Delegate to response processor
        return self.response_processor.get_feedback_statistics()
    
    def remember_fact(self, key: str, value: str = None) -> bool:
        """
        Store a fact about the user in memory.
        
        Args:
            key (str): The fact key or the full fact string if value is None
            value (str): The fact value (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Handle both calling conventions:
        # 1. remember_fact("birthday", "January 1st")
        # 2. remember_fact("birthday: January 1st")
        if value is not None:
            fact = f"{key}: {value}"
        else:
            fact = key
            
        # Delegate to memory service
        return self.memory_service.remember_fact(self.user_id, fact)
    
    def create_plan(self, task_description: str) -> Task:
        """
        Create a plan for a complex task.
        
        Args:
            task_description (str): Description of the complex task
            
        Returns:
            Task: The root task representing the plan
        """
        return self.planning_engine.create_plan(task_description, self.user_id)
    
    def execute_plan(self, plan_id: str) -> bool:
        """
        Execute a plan.
        
        Args:
            plan_id (str): The ID of the plan to execute
            
        Returns:
            bool: True if the plan was found and executed, False otherwise
        """
        return self.planning_engine.execute_plan(plan_id)
    
    def make_decision(self, problem: str, options: List[str],
                     constraints: List[str] = None, preferences: List[str] = None) -> str:
        """
        Make a decision based on the provided context.
        
        Args:
            problem (str): The problem to solve
            options (List[str]): The available options
            constraints (List[str]): Constraints to consider
            preferences (List[str]): Preferences to consider
            
        Returns:
            str: The selected option
        """
        # Convert string options to DecisionOption objects
        decision_options = [
            DecisionOption(id=str(i), description=option)
            for i, option in enumerate(options)
        ]
        
        # Create decision context
        context = DecisionContext(
            problem=problem,
            options=decision_options,
            constraints=constraints or [],
            preferences=preferences or []
        )
        
        # Make decision
        selected_option = self.reasoning_engine.make_decision(context)
        return selected_option.description if selected_option else None
    
    def reason(self, premises: List[str], reasoning_type: str = "deductive") -> str:
        """
        Perform logical reasoning based on premises.
        
        Args:
            premises (List[str]): The premises to reason from
            reasoning_type (str): The type of reasoning to use
            
        Returns:
            str: The conclusion
        """
        # Convert string to ReasoningType enum
        try:
            reasoning_enum = ReasoningType(reasoning_type.lower())
        except ValueError:
            reasoning_enum = ReasoningType.DEDUCTIVE
        
        return self.reasoning_engine.reason(premises, reasoning_enum)
    
    def execute_decision_tree(self, tree_id: str, answers: List[str] = None) -> dict:
        """
        Execute a decision tree.
        
        Args:
            tree_id (str): The ID of the tree to execute
            answers (List[str]): List of answers to guide the traversal
            
        Returns:
            dict: The result of the tree execution
        """
        return self.decision_tree_manager.execute_tree(tree_id, answers)
    
    def list_decision_trees(self) -> List[dict]:
        """
        List all available decision trees.
        
        Returns:
            List[dict]: List of tree information
        """
        return self.decision_tree_manager.list_trees()
    
    def get_plan_status(self, plan_id: str) -> dict:
        """
        Get the status of a plan.
        
        Args:
            plan_id (str): The ID of the plan
            
        Returns:
            dict: The plan status information
        """
        plan = self.planning_engine.get_plan(plan_id)
        if not plan:
            return None
        
        # Count task statuses
        all_tasks = [plan] + plan.get_all_subtasks()
        status_counts = {}
        for task in all_tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "plan_id": plan.id,
            "description": plan.description,
            "status": plan.status.value,
            "total_tasks": len(all_tasks),
            "status_counts": status_counts
        }
    
    def get_error_metrics(self) -> dict:
        """
        Get error metrics for monitoring and analysis.
        
        Returns:
            dict: Error metrics summary
        """
        # Delegate to error handler
        return self.error_handler.get_error_metrics()