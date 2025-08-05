"""
Memory Storage for Personal Agent

This module contains the storage implementations for persisting memory items.
Implements async-first pattern with sync wrappers.
"""

import sqlite3
import json
import os
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiosqlite
from .models import MemoryItem, Conversation, ConversationTurn, Feedback, Entity, Relationship


class MemoryStorage:
    """Abstract base class for memory storage implementations."""
    
    async def save(self, item: MemoryItem) -> bool:
        """Save a memory item."""
        raise NotImplementedError
    
    async def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID."""
        raise NotImplementedError
    
    async def search(self, query: str, type: str = None, limit: int = 10) -> List[MemoryItem]:
        """Search for memory items."""
        raise NotImplementedError
    
    async def delete(self, id: str) -> bool:
        """Delete a memory item."""
        raise NotImplementedError
    
    async def update(self, item: MemoryItem) -> bool:
        """Update an existing memory item."""
        raise NotImplementedError


class AsyncSQLiteMemoryStorage(MemoryStorage):
    """Async-first SQLite implementation of memory storage."""
    
    def __init__(self, db_path: str = "data/memory.db", pool_size: int = 5):
        """
        Initialize the async SQLite memory storage.
        
        Args:
            db_path (str): Path to the SQLite database file
            pool_size (int): Size of the connection pool (default: 5)
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._initialized = False

    async def _init_db(self):
        """Initialize the database with required tables."""
        if self._initialized:
            return
            
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Create tables
            await db.execute('''
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    embedding TEXT
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    turn_index INTEGER,
                    user_id TEXT,
                    rating INTEGER,
                    comment TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    memory_item_id TEXT,
                    type TEXT,
                    value TEXT,
                    confidence REAL,
                    metadata TEXT,
                    FOREIGN KEY (memory_item_id) REFERENCES memory_items (id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_item_id TEXT,
                    source_entity_id TEXT,
                    target_entity_id TEXT,
                    relationship_type TEXT,
                    confidence REAL,
                    metadata TEXT,
                    FOREIGN KEY (memory_item_id) REFERENCES memory_items (id),
                    FOREIGN KEY (source_entity_id) REFERENCES entities (id),
                    FOREIGN KEY (target_entity_id) REFERENCES entities (id)
                )
            ''')
            
            await db.commit()
        
        self._initialized = True

    async def save(self, item: MemoryItem) -> bool:
        """Save a memory item asynchronously."""
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO memory_items 
                    (id, type, content, metadata, created_at, updated_at, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.id,
                    item.type,
                    json.dumps(item.content),
                    json.dumps(item.metadata),
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                    json.dumps(item.embedding) if item.embedding else None
                ))
                
                # Save entities
                for entity in item.entities:
                    await db.execute('''
                        INSERT OR REPLACE INTO entities 
                        (id, memory_item_id, type, value, confidence, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        entity.id,
                        item.id,
                        entity.type,
                        entity.value,
                        entity.confidence,
                        json.dumps(entity.metadata) if entity.metadata else None
                    ))
                
                # Save relationships
                for relationship in item.relationships:
                    await db.execute('''
                        INSERT OR REPLACE INTO relationships 
                        (memory_item_id, source_entity_id, target_entity_id, 
                         relationship_type, confidence, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item.id,
                        relationship.source_entity_id,
                        relationship.target_entity_id,
                        relationship.relationship_type,
                        relationship.confidence,
                        json.dumps(relationship.metadata) if relationship.metadata else None
                    ))
                
                await db.commit()
                return True
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error saving memory item {item.id}: {e}")
            return False

    async def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID asynchronously."""
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute('''
                    SELECT * FROM memory_items WHERE id = ?
                ''', (id,))
                
                row = await cursor.fetchone()
                if not row:
                    return None
                
                # Get entities
                entities_cursor = await db.execute('''
                    SELECT * FROM entities WHERE memory_item_id = ?
                ''', (id,))
                entities_rows = await entities_cursor.fetchall()
                
                entities = []
                for entity_row in entities_rows:
                    entities.append(Entity(
                        id=entity_row['id'],
                        type=entity_row['type'],
                        value=entity_row['value'],
                        confidence=entity_row['confidence'],
                        metadata=json.loads(entity_row['metadata']) if entity_row['metadata'] else None
                    ))
                
                # Get relationships
                relationships_cursor = await db.execute('''
                    SELECT * FROM relationships WHERE memory_item_id = ?
                ''', (id,))
                relationships_rows = await relationships_cursor.fetchall()
                
                relationships = []
                for rel_row in relationships_rows:
                    relationships.append(Relationship(
                        source_entity_id=rel_row['source_entity_id'],
                        target_entity_id=rel_row['target_entity_id'],
                        relationship_type=rel_row['relationship_type'],
                        confidence=rel_row['confidence'],
                        metadata=json.loads(rel_row['metadata']) if rel_row['metadata'] else None
                    ))
                
                return MemoryItem(
                    id=row['id'],
                    type=row['type'],
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    embedding=json.loads(row['embedding']) if row['embedding'] else None,
                    entities=entities,
                    relationships=relationships
                )
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error retrieving memory item {id}: {e}")
            return None

    async def search(self, query: str, type: str = None, limit: int = 10) -> List[MemoryItem]:
        """Search for memory items asynchronously."""
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Build SQL query
                sql = 'SELECT * FROM memory_items WHERE 1=1'
                params = []
                
                # Add type filter if specified
                if type:
                    sql += ' AND type = ?'
                    params.append(type)
                
                # Add content search if query is not empty
                if query is not None and query.strip():
                    sql += ' AND content LIKE ?'
                    params.append(f'%{query}%')
                elif query == "":
                    # If query is explicitly empty and no type filter, return no results
                    # But if there's a type filter, we still want to return results of that type
                    if not type:
                        sql += ' AND 1=0'  # This will always be false, returning no results
                
                sql += ' ORDER BY updated_at DESC LIMIT ?'
                params.append(limit)
                
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
                
                items = []
                for row in rows:
                    # For simplicity, not loading entities/relationships in search
                    # This could be optimized with a single JOIN query if needed
                    items.append(MemoryItem(
                        id=row['id'],
                        type=row['type'],
                        content=json.loads(row['content']),
                        metadata=json.loads(row['metadata']),
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        embedding=json.loads(row['embedding']) if row['embedding'] else None,
                        entities=[],  # Not loaded in search for performance
                        relationships=[]  # Not loaded in search for performance
                    ))
                
                return items
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error searching memory items: {e}")
            return []

    async def delete(self, id: str) -> bool:
        """Delete a memory item asynchronously."""
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete relationships first (foreign key constraint)
                await db.execute('DELETE FROM relationships WHERE memory_item_id = ?', (id,))
                
                # Delete entities
                await db.execute('DELETE FROM entities WHERE memory_item_id = ?', (id,))
                
                # Delete the memory item
                await db.execute('DELETE FROM memory_items WHERE id = ?', (id,))
                
                await db.commit()
                # Check if any rows were affected
                # Note: aiosqlite doesn't directly support rowcount, so we'll check differently
                cursor = await db.execute('SELECT changes()')
                row = await cursor.fetchone()
                changes = row[0] if row else 0
                return changes > 0
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error deleting memory item {id}: {e}")
            return False

    async def update(self, item: MemoryItem) -> bool:
        """Update an existing memory item asynchronously."""
        item.updated_at = datetime.now()
        return await self.save(item)

    # Conversation-specific methods
    async def save_conversation(self, conversation: Conversation) -> bool:
        """Save a conversation asynchronously."""
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (id, user_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    conversation.id,
                    conversation.user_id,
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat()
                ))
                
                # Delete existing turns and re-insert (simpler than update logic)
                await db.execute('DELETE FROM conversation_turns WHERE conversation_id = ?', (conversation.id,))
                
                for turn in conversation.turns:
                    await db.execute('''
                        INSERT INTO conversation_turns 
                        (conversation_id, role, content, timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        conversation.id,
                        turn.role,
                        turn.content,
                        turn.timestamp.isoformat(),
                        json.dumps(turn.metadata)
                    ))
                
                await db.commit()
                return True
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error saving conversation {conversation.id}: {e}")
            return False
    
    async def save_conversation_turn(self, user_id: str, user_input: str, agent_response: str) -> bool:
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
            # Create conversation turn items
            conversation = Conversation(user_id=user_id)
            conversation.turns.append(ConversationTurn(
                role="user",
                content=user_input
            ))
            conversation.turns.append(ConversationTurn(
                role="assistant",
                content=agent_response
            ))
            
            # Create memory item
            memory_item = MemoryItem(
                type="conversation",
                content={
                    "conversation_id": conversation.id,
                    "user_id": user_id,
                    "turns": [
                        {
                            "role": turn.role,
                            "content": turn.content,
                            "timestamp": turn.timestamp.isoformat()
                        }
                        for turn in conversation.turns
                    ]
                }
            )
            
            return await self.save(memory_item)
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error saving conversation turn: {e}")
            return False
    
    async def save_feedback(self, feedback) -> bool:
        """
        Save feedback item asynchronously.
        
        Args:
            feedback: Feedback data to save (can be Dict or Feedback object)
            
        Returns:
            bool: True if successful, False otherwise
        """
        await self._init_db()
        
        # Convert Feedback object to dictionary if needed
        if hasattr(feedback, '__dict__'):
            feedback_dict = {
                'id': getattr(feedback, 'id', None),
                'conversation_id': getattr(feedback, 'conversation_id', None),
                'turn_index': None,  # Not used in Feedback model
                'user_id': getattr(feedback, 'user_id', None),
                'rating': getattr(feedback, 'rating', None),
                'comment': getattr(feedback, 'comment', None),
                'timestamp': getattr(feedback, 'created_at', None)
            }
        else:
            feedback_dict = feedback
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Build dynamic query based on available fields
                fields = ['id', 'conversation_id', 'user_id', 'rating', 'comment']
                values = [
                    feedback_dict.get('id'),
                    feedback_dict.get('conversation_id'),
                    feedback_dict.get('user_id'),
                    feedback_dict.get('rating'),
                    feedback_dict.get('comment')
                ]
                
                # Add turn_index only if it's not None
                if feedback_dict.get('turn_index') is not None:
                    fields.append('turn_index')
                    values.append(feedback_dict.get('turn_index'))
                
                # Add timestamp only if it's not None
                if feedback_dict.get('timestamp') is not None:
                    fields.append('timestamp')
                    # Convert datetime to string if it's a datetime object
                    timestamp = feedback_dict.get('timestamp')
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat()
                    values.append(timestamp)
                
                # Create placeholders for the query
                placeholders = ', '.join(['?' for _ in fields])
                field_names = ', '.join(fields)
                
                await db.execute(f'''
                    INSERT OR REPLACE INTO feedback
                    ({field_names})
                    VALUES ({placeholders})
                ''', values)
                
                await db.commit()
                return True
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error saving feedback: {e}")
            return False
    
    async def get_feedback(self, message_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get feedback items asynchronously.
        
        Args:
            message_id (str): Optional message ID to filter feedback
            limit (int): Maximum number of feedback items to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of feedback items
        """
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if message_id:
                    cursor = await db.execute('''
                        SELECT * FROM feedback
                        WHERE id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (message_id, limit))
                else:
                    cursor = await db.execute('''
                        SELECT * FROM feedback
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (limit,))
                
                rows = await cursor.fetchall()
                
                feedback_items = []
                for row in rows:
                    feedback_items.append({
                        'id': row['id'],
                        'conversation_id': row['conversation_id'],
                        'turn_index': row['turn_index'],
                        'user_id': row['user_id'],
                        'rating': row['rating'],
                        'comment': row['comment'],
                        'timestamp': row['timestamp']
                    })
                
                return feedback_items
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error retrieving feedback: {e}")
            return []
    
    async def get_feedback_stats(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get feedback statistics asynchronously.
        
        Args:
            user_id (str): Optional user ID to filter feedback
            
        Returns:
            Dict[str, Any]: Feedback statistics
        """
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                if user_id:
                    cursor = await db.execute('''
                        SELECT
                            COUNT(*) as total_feedback,
                            AVG(rating) as average_rating,
                            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback,
                            COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_feedback
                        FROM feedback
                        WHERE user_id = ?
                    ''', (user_id,))
                else:
                    cursor = await db.execute('''
                        SELECT
                            COUNT(*) as total_feedback,
                            AVG(rating) as average_rating,
                            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback,
                            COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_feedback
                        FROM feedback
                    ''')
                
                row = await cursor.fetchone()
                
                if row:
                    return {
                        'total_feedback': row['total_feedback'] or 0,
                        'average_rating': round(row['average_rating'] or 0, 2),
                        'positive_feedback': row['positive_feedback'] or 0,
                        'negative_feedback': row['negative_feedback'] or 0
                    }
                else:
                    return {
                        'total_feedback': 0,
                        'average_rating': 0,
                        'positive_feedback': 0,
                        'negative_feedback': 0
                    }
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error retrieving feedback stats: {e}")
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'positive_feedback': 0,
                'negative_feedback': 0
            }
    
    async def get_conversation_history(self, limit: int = 10) -> List[MemoryItem]:
        """
        Get recent conversation history asynchronously.
        
        Args:
            limit (int): Maximum number of conversation items to retrieve
            
        Returns:
            List[MemoryItem]: List of recent conversation memory items
        """
        await self._init_db()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute('''
                    SELECT * FROM memory_items
                    WHERE type = 'conversation'
                    ORDER BY updated_at DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = await cursor.fetchall()
                
                items = []
                for row in rows:
                    # Get entities
                    entities_cursor = await db.execute('''
                        SELECT * FROM entities WHERE memory_item_id = ?
                    ''', (row['id'],))
                    entities_rows = await entities_cursor.fetchall()
                    
                    entities = []
                    for entity_row in entities_rows:
                        entities.append(Entity(
                            id=entity_row['id'],
                            type=entity_row['type'],
                            value=entity_row['value'],
                            confidence=entity_row['confidence'],
                            metadata=json.loads(entity_row['metadata']) if entity_row['metadata'] else None
                        ))
                    
                    # Get relationships
                    relationships_cursor = await db.execute('''
                        SELECT * FROM relationships WHERE memory_item_id = ?
                    ''', (row['id'],))
                    relationships_rows = await relationships_cursor.fetchall()
                    
                    relationships = []
                    for rel_row in relationships_rows:
                        relationships.append(Relationship(
                            source_entity_id=rel_row['source_entity_id'],
                            target_entity_id=rel_row['target_entity_id'],
                            relationship_type=rel_row['relationship_type'],
                            confidence=rel_row['confidence'],
                            metadata=json.loads(rel_row['metadata']) if rel_row['metadata'] else None
                        ))
                    
                    items.append(MemoryItem(
                        id=row['id'],
                        type=row['type'],
                        content=json.loads(row['content']),
                        metadata=json.loads(row['metadata']),
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at']),
                        embedding=json.loads(row['embedding']) if row['embedding'] else None,
                        entities=entities,
                        relationships=relationships
                    ))
                
                return items
                
        except Exception as e:
            from ..utils.logging import get_logger
            logger = get_logger()
            logger.error(f"Error retrieving conversation history: {e}")
            return []


class SQLiteMemoryStorage:
    """Synchronous wrapper around AsyncSQLiteMemoryStorage."""
    
    def __init__(self, db_path: str = "data/memory.db", pool_size: int = 5):
        self.async_storage = AsyncSQLiteMemoryStorage(db_path, pool_size)
        self.db_path = db_path  # Add db_path property for compatibility
        self.pool_size = pool_size  # Add pool_size property for compatibility
        self._loop = None

    def _run_async(self, coro):
        """
        Run an async coroutine in sync context.
        
        This method handles the complexity of running async code from sync code
        by detecting the current async context and choosing the appropriate execution method.
        """
        try:
            # Check if we're already in an async context
            asyncio.get_running_loop()
            # If we reach here, we're in an async context - we cannot use asyncio.run()
            # Instead, we need to schedule the coroutine in a thread with a new event loop
            import concurrent.futures
            
            # Create a dedicated thread for running the async operation
            def run_in_thread():
                return asyncio.run(coro)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="async_storage") as executor:
                future = executor.submit(run_in_thread)
                return future.result()
                
        except RuntimeError:
            # No event loop is running - we can safely use asyncio.run()
            return asyncio.run(coro)

    def save(self, item: MemoryItem) -> bool:
        """Save a memory item synchronously."""
        return self._run_async(self.async_storage.save(item))

    def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID synchronously."""
        return self._run_async(self.async_storage.retrieve(id))

    def search(self, query: str, type: str = None, limit: int = 10) -> List[MemoryItem]:
        """Search for memory items synchronously."""
        return self._run_async(self.async_storage.search(query, type, limit))

    def delete(self, id: str) -> bool:
        """Delete a memory item synchronously."""
        return self._run_async(self.async_storage.delete(id))

    def update(self, item: MemoryItem) -> bool:
        """Update an existing memory item synchronously."""
        return self._run_async(self.async_storage.update(item))

    def save_conversation(self, conversation: Conversation) -> bool:
        """Save a conversation synchronously."""
        return self._run_async(self.async_storage.save_conversation(conversation))
    
    def save_conversation_turn(self, user_id: str, user_input: str, agent_response: str) -> bool:
        """Save a conversation turn synchronously."""
        return self._run_async(self.async_storage.save_conversation_turn(user_id, user_input, agent_response))
    
    def save_feedback(self, feedback) -> bool:
        """Save feedback synchronously."""
        return self._run_async(self.async_storage.save_feedback(feedback))
    
    def get_feedback(self, message_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get feedback items synchronously."""
        return self._run_async(self.async_storage.get_feedback(message_id, limit))
    
    def get_feedback_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get feedback statistics synchronously."""
        return self._run_async(self.async_storage.get_feedback_stats(user_id))
    
    def get_conversation_history(self, limit: int = 10) -> List[MemoryItem]:
        """Get recent conversation history synchronously."""
        return self._run_async(self.async_storage.get_conversation_history(limit))