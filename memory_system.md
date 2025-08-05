# Data Storage and Memory Functionality

## Overview
The memory system provides persistent storage for the personal agent's knowledge, conversation history, and learned preferences. It's designed to be flexible, scalable, and efficient.

## Memory Types

### 1. Conversation Memory
- Stores the history of interactions with users
- Maintains context for ongoing conversations
- Includes timestamps and metadata

### 2. Knowledge Memory
- Long-term storage of facts and information
- Learned preferences and user-specific data
- Semantic search capabilities

### 3. Task Memory
- Records of completed tasks and their outcomes
- Task execution history and performance metrics
- Template storage for recurring tasks

### 4. Skill Memory
- Records of learned skills and capabilities
- Performance data for different tools
- Adaptation preferences

## Data Models

### Memory Item (`src/personal_agent/memory/models.py`)

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

@dataclass
class MemoryItem:
    id: str = None
    type: str = "conversation"  # conversation, knowledge, task, skill
    content: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    embedding: Optional[list] = None  # For semantic search
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.content is None:
            self.content = {}
        if self.metadata is None:
            self.metadata = {}
```

### Conversation Models

```python
@dataclass
class ConversationTurn:
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class Conversation:
    id: str
    user_id: str
    turns: list[ConversationTurn]
    created_at: datetime
    updated_at: datetime
```

## Storage Backends

### SQLite Backend (Default)
The default storage backend uses SQLite for simplicity and ease of deployment.

#### Schema
```sql
CREATE TABLE memory_items (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,  -- JSON serialized
    metadata TEXT,          -- JSON serialized
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    embedding BLOB          -- Optional vector embedding
);

CREATE INDEX idx_memory_type ON memory_items(type);
CREATE INDEX idx_memory_created ON memory_items(created_at);
```

### Future Backend Options
1. **PostgreSQL** - For production deployments requiring high availability
2. **MongoDB** - For document-based storage with flexible schema
3. **Vector Database** - For semantic search capabilities (Pinecone, Weaviate)
4. **File-based** - Simple JSON file storage for development

## Memory Management System (`src/personal_agent/memory/storage.py`)

### Storage Interface
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import MemoryItem

class MemoryStorage(ABC):
    @abstractmethod
    def save(self, item: MemoryItem) -> bool:
        """Save a memory item."""
        pass
    
    @abstractmethod
    def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID."""
        pass
    
    @abstractmethod
    def search(self, query: str, type: str = None, limit: int = 10) -> List[MemoryItem]:
        """Search for memory items."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a memory item."""
        pass
    
    @abstractmethod
    def update(self, item: MemoryItem) -> bool:
        """Update an existing memory item."""
        pass
```

### SQLite Implementation
```python
import sqlite3
import json
from typing import List, Optional
from .models import MemoryItem

class SQLiteMemoryStorage(MemoryStorage):
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_items(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_created ON memory_items(created_at)")
    
    def save(self, item: MemoryItem) -> bool:
        """Save a memory item."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memory_items 
                    (id, type, content, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item.id,
                    item.type,
                    json.dumps(item.content),
                    json.dumps(item.metadata),
                    item.created_at.isoformat(),
                    item.updated_at.isoformat() if item.updated_at else item.created_at.isoformat()
                ))
            return True
        except Exception as e:
            print(f"Error saving memory item: {e}")
            return False
    
    def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM memory_items WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return MemoryItem(
                    id=row[0],
                    type=row[1],
                    content=json.loads(row[2]),
                    metadata=json.loads(row[3]) if row[3] else {},
                    created_at=datetime.fromisoformat(row[4]),
                    updated_at=datetime.fromisoformat(row[5])
                )
        return None
```

## Memory Retrieval Strategies

### 1. Exact Match Retrieval
- Direct lookup by ID
- Fastest retrieval method
- Used for specific memory items

### 2. Chronological Retrieval
- Retrieve memories by time range
- Useful for conversation history
- Supports pagination

### 3. Type-based Retrieval
- Retrieve memories of specific types
- Filter by memory category
- Supports combination with other filters

### 4. Semantic Search (Future)
- Vector-based similarity search
- Requires embedding generation
- Most relevant for knowledge memories

## Memory Lifecycle Management

### Retention Policies
1. **Conversation History** - Keep last N conversations
2. **Knowledge Base** - Persistent with periodic cleanup
3. **Task Records** - Keep for X days then archive
4. **Skill Data** - Persistent with performance-based retention

### Memory Cleanup
- Periodic cleanup of expired memories
- Archival of old data to separate storage
- Compression of infrequently accessed memories

## Privacy and Security

### Data Encryption
- Optional encryption of sensitive memory content
- Key management for encryption keys
- Transparent encryption/decryption

### Access Control
- User-specific memory isolation
- Permission-based access to memory items
- Audit logging for memory access

### Data Deletion
- Complete removal of memory items
- Secure deletion options
- GDPR compliance support

## Performance Considerations

### Caching
- In-memory cache for frequently accessed memories
- LRU eviction policy
- Cache warming for common queries

### Indexing
- Database indexes for common query patterns
- Full-text search for content
- Custom indexes for metadata fields

### Batch Operations
- Bulk save and retrieve operations
- Transaction support for consistency
- Asynchronous operations for non-blocking performance

## Integration with Core Modules

### Agent Integration
- Automatic memory persistence during conversations
- Context retrieval for maintaining conversation flow
- Memory-based personalization of responses

### LLM Integration
- Memory context injection in prompts
- Learning from conversation outcomes
- Feedback-based memory updates

### Tool Integration
- Task result storage in memory
- Tool performance tracking
- Adaptive tool selection based on memory