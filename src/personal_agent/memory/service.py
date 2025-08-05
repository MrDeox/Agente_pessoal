"""
Memory Service for Personal Agent

This module contains the MemoryService class that manages all memory-related operations,
including conversation history, knowledge storage, and context retrieval.
"""

from typing import List, Dict, Any, Optional
from ..memory.storage import SQLiteMemoryStorage, AsyncSQLiteMemoryStorage
from ..memory.models import MemoryItem
from ..config.settings import Config
from ..context.processor import ContextProcessor
from ..utils.logging import get_logger
import asyncio


class MemoryService:
    """
    Manages all memory-related operations for the agent.
    """
    
    def __init__(self, config: Config = None, memory_storage=None):
        """
        Initialize the memory service.
        
        Args:
            config (Config): Configuration object
            memory_storage: Memory storage instance (can be sync or async)
        """
        self.config = config or Config.load()
        # If no storage is provided, create a default sync storage
        if memory_storage is None:
            self.storage = SQLiteMemoryStorage(self.config.memory.database_path)
        else:
            self.storage = memory_storage
        self.context_processor = ContextProcessor()
        self.logger = get_logger()
    
    def save_conversation_turn(self, user_id: str, user_input: str, agent_response: str) -> bool:
        """
        Save a conversation turn to memory.
        
        Args:
            user_id (str): ID of the user
            user_input (str): User's input message
            agent_response (str): Agent's response
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract entities and relationships from user input
            user_entities = self.context_processor.extract_entities(user_input)
            user_relationships = self.context_processor.extract_relationships(user_entities, user_input)
            
            # Extract entities and relationships from agent response
            agent_entities = self.context_processor.extract_entities(agent_response)
            agent_relationships = self.context_processor.extract_relationships(agent_entities, agent_response)
            
            # Combine all entities and relationships
            all_entities = user_entities + agent_entities
            all_relationships = user_relationships + agent_relationships
            
            # Create memory item
            memory_item = MemoryItem(
                type="conversation",
                content={
                    "user_id": user_id,
                    "turns": [
                        {
                            "role": "user",
                            "content": user_input
                        },
                        {
                            "role": "assistant",
                            "content": agent_response
                        }
                    ]
                },
                entities=all_entities,
                relationships=all_relationships
            )
            
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving conversation turn: {e}")
            return False
    
    async def save_conversation_turn_async(self, user_id: str, user_input: str, agent_response: str) -> bool:
        """
        Save a conversation turn to memory asynchronously.
        
        Args:
            user_id (str): ID of the user
            user_input (str): User's input message
            agent_response (str): Agent's response
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract entities and relationships from user input
            user_entities = self.context_processor.extract_entities(user_input)
            user_relationships = self.context_processor.extract_relationships(user_entities, user_input)
            
            # Extract entities and relationships from agent response
            agent_entities = self.context_processor.extract_entities(agent_response)
            agent_relationships = self.context_processor.extract_relationships(agent_entities, agent_response)
            
            # Combine all entities and relationships
            all_entities = user_entities + agent_entities
            all_relationships = user_relationships + agent_relationships
            
            # Create memory item
            memory_item = MemoryItem(
                type="conversation",
                content={
                    "user_id": user_id,
                    "turns": [
                        {
                            "role": "user",
                            "content": user_input
                        },
                        {
                            "role": "assistant",
                            "content": agent_response
                        }
                    ]
                },
                entities=all_entities,
                relationships=all_relationships
            )
            
            # Check if storage supports async operations
            if hasattr(self.storage, 'save') and callable(getattr(self.storage, 'save')):
                # If it's our new async storage, call it directly
                if hasattr(self.storage, '__class__') and 'AsyncSQLiteMemoryStorage' in str(self.storage.__class__):
                    return await self.storage.save(memory_item)
                # If it's our new sync storage with async methods, call them directly
                elif hasattr(self.storage, '__class__') and 'SQLiteMemoryStorage' in str(self.storage.__class__):
                    return self.storage.save(memory_item)
            
            # Fallback to sync method
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving conversation turn: {e}")
            return False
    
    def get_memory_context(self, user_id: str, conversation_history: List[Dict[str, str]], 
                          last_user_input: str = "") -> str:
        """
        Retrieve relevant context from memory to inform responses.
        
        Args:
            user_id (str): ID of the user
            conversation_history (List[Dict[str, str]]): Recent conversation history
            last_user_input (str): Last user input for relevance scoring
            
        Returns:
            str: Formatted context from memory
        """
        context_parts = []
        
        # Add conversation history
        try:
            # Try to use the more efficient method first
            if hasattr(self.storage, 'get_conversation_history'):
                recent_memories = self.storage.get_conversation_history(limit=5)
                recent_turns = []
                for memory in recent_memories:
                    recent_turns.extend(memory.content.get("turns", []))
            else:
                # Fallback to search method
                recent_memories = self.storage.search("", type="conversation", limit=5)
                recent_turns = []
                for memory in recent_memories:
                    recent_turns.extend(memory.content.get("turns", []))
        except Exception as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            recent_turns = []
        
        if recent_turns:
            conversation_context = "Recent conversation history:\n"
            for turn in recent_turns:
                conversation_context += f"{turn['role']}: {turn['content']}\n"
            context_parts.append(conversation_context)
        
        # Add knowledge items (preferences and facts)
        try:
            knowledge_items = self.storage.search("", type="knowledge", limit=10)
            
            # Use context processor to score relevance of knowledge items
            if knowledge_items and last_user_input:
                # Score context relevance
                scored_items = self.context_processor.score_context_relevance(last_user_input, knowledge_items)
                # Sort by relevance score and take top items
                knowledge_items = [item for item, score in scored_items[:5]]  # Top 5 most relevant
            
            if knowledge_items:
                knowledge_context = "User knowledge:\n"
                for item in knowledge_items:
                    if "preference" in item.content:
                        knowledge_context += f"Preference: {item.content['preference']}\n"
                    elif "fact" in item.content:
                        knowledge_context += f"Fact: {item.content['fact']}\n"
                context_parts.append(knowledge_context)
        except Exception as e:
            self.logger.error(f"Error retrieving knowledge items: {e}")
        
        # Combine all context parts
        if context_parts:
            return "\n".join(context_parts)
        else:
            return ""
    
    def remember_preference(self, user_id: str, preference: str) -> bool:
        """
        Store a user preference in memory.
        
        Args:
            user_id (str): ID of the user
            preference (str): The user preference to remember
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            memory_item = MemoryItem(
                type="knowledge",
                content={"preference": preference},
                metadata={"user_id": user_id, "category": "preference"}
            )
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving preference: {e}")
            return False
    
    async def remember_preference_async(self, user_id: str, preference: str) -> bool:
        """
        Store a user preference in memory asynchronously.
        
        Args:
            user_id (str): ID of the user
            preference (str): The user preference to remember
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            memory_item = MemoryItem(
                type="knowledge",
                content={"preference": preference},
                metadata={"user_id": user_id, "category": "preference"}
            )
            
            # Check if storage supports async operations
            if hasattr(self.storage, 'save') and callable(getattr(self.storage, 'save')):
                # If it's our new async storage, call it directly
                if hasattr(self.storage, '__class__') and 'AsyncSQLiteMemoryStorage' in str(self.storage.__class__):
                    return await self.storage.save(memory_item)
                # If it's our new sync storage with async methods, call them directly
                elif hasattr(self.storage, '__class__') and 'SQLiteMemoryStorage' in str(self.storage.__class__):
                    return self.storage.save(memory_item)
            
            # Fallback to sync method
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving preference: {e}")
            return False
    
    def remember_fact(self, user_id: str, fact: str) -> bool:
        """
        Store a fact about the user in memory.
        
        Args:
            user_id (str): ID of the user
            fact (str): The fact to remember
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            memory_item = MemoryItem(
                type="knowledge",
                content={"fact": fact},
                metadata={"user_id": user_id, "category": "fact"}
            )
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving fact: {e}")
            return False
    
    async def remember_fact_async(self, user_id: str, fact: str) -> bool:
        """
        Store a fact about the user in memory asynchronously.
        
        Args:
            user_id (str): ID of the user
            fact (str): The fact to remember
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            memory_item = MemoryItem(
                type="knowledge",
                content={"fact": fact},
                metadata={"user_id": user_id, "category": "fact"}
            )
            
            # Check if storage supports async operations
            if hasattr(self.storage, 'save') and callable(getattr(self.storage, 'save')):
                # If it's our new async storage, call it directly
                if hasattr(self.storage, '__class__') and 'AsyncSQLiteMemoryStorage' in str(self.storage.__class__):
                    return await self.storage.save(memory_item)
                # If it's our new sync storage with async methods, call them directly
                elif hasattr(self.storage, '__class__') and 'SQLiteMemoryStorage' in str(self.storage.__class__):
                    return self.storage.save(memory_item)
            
            # Fallback to sync method
            return self.storage.save(memory_item)
        except Exception as e:
            self.logger.error(f"Error saving fact: {e}")
            return False
    
    def search_knowledge(self, query: str, user_id: str = None, limit: int = 10) -> List[MemoryItem]:
        """
        Search for knowledge items in memory.
        
        Args:
            query (str): Search query
            user_id (str): Optional user ID to filter results
            limit (int): Maximum number of results to return
            
        Returns:
            List[MemoryItem]: List of matching knowledge items
        """
        try:
            # Search for knowledge items
            results = self.storage.search(query, type="knowledge", limit=limit)
            
            # If user_id is specified, filter results
            if user_id:
                results = [
                    item for item in results 
                    if item.metadata and item.metadata.get("user_id") == user_id
                ]
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching knowledge: {e}")
            return []
    
    async def search_knowledge_async(self, query: str, user_id: str = None, limit: int = 10) -> List[MemoryItem]:
        """
        Search for knowledge items in memory asynchronously.
        
        Args:
            query (str): Search query
            user_id (str): Optional user ID to filter results
            limit (int): Maximum number of results to return
            
        Returns:
            List[MemoryItem]: List of matching knowledge items
        """
        try:
            # Check if storage supports async operations
            if hasattr(self.storage, 'search') and callable(getattr(self.storage, 'search')):
                # If it's our new async storage, call it directly
                if hasattr(self.storage, '__class__') and 'AsyncSQLiteMemoryStorage' in str(self.storage.__class__):
                    results = await self.storage.search(query, type="knowledge", limit=limit)
                # If it's our new sync storage with async methods, call them directly
                elif hasattr(self.storage, '__class__') and 'SQLiteMemoryStorage' in str(self.storage.__class__):
                    results = self.storage.search(query, type="knowledge", limit=limit)
                else:
                    results = self.storage.search(query, type="knowledge", limit=limit)
            else:
                results = self.storage.search(query, type="knowledge", limit=limit)
            
            # If user_id is specified, filter results
            if user_id:
                results = [
                    item for item in results 
                    if item.metadata and item.metadata.get("user_id") == user_id
                ]
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching knowledge: {e}")
            return []
    
    def get_recent_conversation_history(self, limit: int = 5) -> List[MemoryItem]:
        """
        Get recent conversation history.
        
        Args:
            limit (int): Maximum number of conversation items to retrieve
            
        Returns:
            List[MemoryItem]: List of recent conversation memory items
        """
        try:
            return self.storage.get_conversation_history(limit=limit)
        except Exception as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    async def get_recent_conversation_history_async(self, limit: int = 5) -> List[MemoryItem]:
        """
        Get recent conversation history asynchronously.
        
        Args:
            limit (int): Maximum number of conversation items to retrieve
            
        Returns:
            List[MemoryItem]: List of recent conversation memory items
        """
        try:
            # Check if storage supports async operations
            if hasattr(self.storage, 'get_conversation_history') and callable(getattr(self.storage, 'get_conversation_history')):
                # If it's our new async storage, call it directly
                if hasattr(self.storage, '__class__') and 'AsyncSQLiteMemoryStorage' in str(self.storage.__class__):
                    return await self.storage.get_conversation_history(limit=limit)
                # If it's our new sync storage with async methods, call them directly
                elif hasattr(self.storage, '__class__') and 'SQLiteMemoryStorage' in str(self.storage.__class__):
                    return self.storage.get_conversation_history(limit=limit)
                else:
                    return self.storage.get_conversation_history(limit=limit)
            else:
                return self.storage.get_conversation_history(limit=limit)
        except Exception as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            return []