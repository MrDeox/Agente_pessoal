"""
Common utility functions for the Personal Agent project.

This module contains shared utility functions that are used across multiple modules
to reduce code duplication and improve maintainability.
"""

from typing import Optional, Any, Dict
import uuid
from .logging import get_logger, log_exception


def generate_id() -> str:
    """
    Generate a unique ID string.
    
    Returns:
        str: A unique ID string
    """
    return str(uuid.uuid4())


def find_conversation_id(conversation_history: list, message_id: str) -> Optional[str]:
    """
    Find the conversation ID for a specific message in the conversation history.
    
    Args:
        conversation_history (list): List of conversation turns
        message_id (str): ID of the message to find
        
    Returns:
        Optional[str]: Conversation ID if found, None otherwise
    """
    if not conversation_history:
        return None
        
    # Find the conversation turn that contains this message
    for turn in reversed(conversation_history):
        if turn.get("id") == message_id:
            return turn.get("conversation_id")
    return None


def safe_call(func, *args, operation_name: str = "operation", 
              success_message: str = None, failure_message: str = None,
              return_on_error: Any = False) -> Any:
    """
    Safely call a function with error handling and logging.
    
    Args:
        func: Function to call
        *args: Arguments to pass to the function
        operation_name (str): Name of the operation for logging
        success_message (str): Message to log on success (optional)
        failure_message (str): Message to log on failure (optional)
        return_on_error (Any): Value to return if the function fails
        
    Returns:
        Any: Result of the function call or return_on_error if it fails
    """
    logger = get_logger()
    try:
        result = func(*args)
        if success_message:
            logger.info(success_message)
        return result
    except Exception as e:
        if failure_message:
            logger.warning(failure_message)
        else:
            log_exception(e, operation_name)
        return return_on_error


def validate_and_log_result(result: bool, operation_name: str, 
                           success_message: str = None, failure_message: str = None) -> bool:
    """
    Log the result of an operation.
    
    Args:
        result (bool): Result of the operation
        operation_name (str): Name of the operation for logging
        success_message (str): Message to log on success (optional)
        failure_message (str): Message to log on failure (optional)
        
    Returns:
        bool: The result that was passed in
    """
    logger = get_logger()
    if result:
        if success_message:
            logger.info(success_message)
        else:
            logger.info(f"{operation_name} completed successfully")
    else:
        if failure_message:
            logger.warning(failure_message)
        else:
            logger.warning(f"{operation_name} failed")
    return result