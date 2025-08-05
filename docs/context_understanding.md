# Context Understanding and Utilization

## Overview

This document describes the improved context understanding and utilization capabilities implemented in the personal agent. These enhancements allow the agent to better understand and utilize context from various sources while maintaining backward compatibility with existing functionality.

## Features Implemented

### 1. Context-Aware Prompt Engineering Techniques

The agent now uses context-aware prompt engineering to create more effective prompts for the LLM. This includes:

- Dynamic system prompts that adapt based on the conversation context
- Better organization of conversation history in prompts
- Clear instructions for the LLM on how to use context information

### 2. Entity Extraction and Relationship Mapping

The agent can now extract entities and relationships from conversations:

- **Entity Extraction**: Identifies named entities such as people, organizations, locations, dates, etc.
- **Relationship Mapping**: Identifies relationships between extracted entities
- **Storage**: Entities and relationships are stored in the memory system for future reference

### 3. Context Relevance Scoring System

A context relevance scoring system helps the agent determine which pieces of context are most relevant to the current conversation:

- Scores context items based on keyword overlap, type relevance, and recency
- Prioritizes the most relevant context when generating responses
- Improves response accuracy by focusing on relevant information

### 4. Enhanced Memory System

The memory system has been enhanced to better utilize context:

- **Entity and Relationship Storage**: Memory items now include extracted entities and relationships
- **Context-Aware Storage**: Conversation turns are stored with their associated entities and relationships
- **Backward Compatibility**: Existing memory items without entities/relationships are handled gracefully

### 5. Integration with Existing Agent

The improved context understanding has been seamlessly integrated with the existing agent:

- **Automatic Entity Extraction**: Entities and relationships are automatically extracted from conversations
- **Context-Aware Response Generation**: The agent uses context-aware prompts when generating responses
- **Relevance-Based Context Retrieval**: The agent retrieves the most relevant context when generating responses

## Implementation Details

### Context Processor

The `ContextProcessor` class in `src/personal_agent/context/processor.py` provides the core functionality for context understanding:

- `create_context_aware_prompt()`: Creates context-aware prompts for the LLM
- `extract_entities()`: Extracts entities from text
- `extract_relationships()`: Extracts relationships between entities
- `score_context_relevance()`: Scores the relevance of context items
- `enhance_memory_with_context()`: Enhances memory items with extracted context

### Memory Models

The memory models in `src/personal_agent/memory/models.py` have been enhanced to include entities and relationships:

- `MemoryItem`: Now includes `entities` and `relationships` fields
- `ConversationTurn`: Now includes `entities` and `relationships` fields
- `Conversation`: Now includes `entities` and `relationships` fields

### Memory Storage

The SQLite memory storage in `src/personal_agent/memory/storage.py` has been updated to handle the new entity and relationship fields:

- Automatic migration to add `entities` and `relationships` columns
- Backward compatibility with existing memory items
- Enhanced `save_conversation_turn()` method that extracts and stores entities and relationships

### Agent Integration

The agent in `src/personal_agent/core/agent.py` has been updated to use the new context understanding capabilities:

- Initialization of the `ContextProcessor`
- Context-aware prompt generation in `_generate_llm_response()`
- Relevance-based context retrieval in `get_memory_context()`

## Testing

A test script `scripts/test_context_understanding.py` demonstrates the new capabilities:

- Basic conversation with entity extraction
- Follow-up questions that require context
- Context relevance scoring
- Complex context with relationships
- Context-aware prompt engineering

## Usage Examples

### Entity Extraction

```python
from personal_agent.context.processor import ContextProcessor

context_processor = ContextProcessor()
text = "John Smith works at ABC Corporation in New York City."
entities = context_processor.extract_entities(text)
# Extracts entities like "John Smith" (person), "ABC Corporation" (organization), "New York City" (location)
```

### Context-Aware Prompts

```python
from personal_agent.context.processor import ContextProcessor

context_processor = ContextProcessor()
messages = context_processor.create_context_aware_prompt(
    user_input="Where do I work?",
    conversation_history=[{"role": "user", "content": "My name is John Smith and I work at ABC Corporation."}],
    memory_context="User knowledge: John Smith is a software engineer"
)
# Creates a context-aware prompt for the LLM
```

### Context Relevance Scoring

```python
from personal_agent.context.processor import ContextProcessor
from personal_agent.memory.models import MemoryItem

context_processor = ContextProcessor()
user_input = "What programming language does John prefer?"
context_items = [MemoryItem(content={"preference": "John prefers Python"})]
scored_items = context_processor.score_context_relevance(user_input, context_items)
# Scores the relevance of context items to the user input
```

## Benefits

1. **Improved Response Accuracy**: The agent can better understand and respond to user queries by leveraging relevant context
2. **Enhanced Context Utilization**: The agent makes better use of stored context information
3. **Better Entity Understanding**: The agent can identify and track important entities in conversations
4. **Relationship Awareness**: The agent can understand relationships between entities
5. **Backward Compatibility**: Existing functionality continues to work as before

## Future Improvements

1. **Advanced Entity Resolution**: Improve entity resolution to handle coreferences and aliases
2. **Semantic Search**: Implement semantic search for context retrieval
3. **Dynamic Context Window**: Dynamically adjust the context window based on relevance
4. **Context Summarization**: Summarize long conversation histories for better context management
5. **Multi-Modal Context**: Extend context understanding to include images, audio, and other modalities