# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup & Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment (if exists)
source venv/bin/activate
```

### Code Quality & Linting
```bash
# Run comprehensive code quality checks
./scripts/run_all_quality_checks.sh

# Run flake8 only
./scripts/run_code_quality_checks.sh
# or
flake8 src/
```

### Testing

#### End-to-End Tests
```bash
# Run all E2E tests
python scripts/run_e2e_tests.py

# Run specific test suites
python scripts/run_e2e_tests.py --suites conversation_flow memory_functionality

# List available test suites
python scripts/run_e2e_tests.py --list-suites

# Run individual test files
python tests/e2e/test_conversation_flow.py
```

#### Unit Tests (using pytest)
```bash
# Run unit tests
pytest tests/unit/

# Run specific test modules
pytest tests/unit/config/test_settings.py
```

#### Integration Tests
```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test categories
pytest tests/integration/memory/
pytest tests/integration/llm/
pytest tests/integration/core/
pytest tests/integration/utils/

# Run individual integration tests
python tests/integration/memory/test_basic_memory.py
python tests/integration/llm/test_llm.py
python tests/integration/core/test_agent_manager.py
```

### Running the Agent
```bash
# Run the interactive agent
python scripts/run_agent.py

# Set environment variables for LLM providers
export PA_LLM__API_KEY="your-api-key"
export PA_LLM__PROVIDER="openrouter"  # or "openai"
export PA_LLM__MODEL="qwen/qwen3-coder:free"

# Using the OpenRouter script
./scripts/run_agent_openrouter.sh
```

## Architecture Overview

This is a Personal AI Agent system with the following layered architecture:

### Core Components

1. **Agent (`src/personal_agent/core/agent.py`)** - Main orchestrator that coordinates all subsystems
2. **AgentManager (`src/personal_agent/core/manager.py`)** - Handles agent lifecycle and management
3. **ComponentFactory (`src/personal_agent/core/factory.py`)** - Creates and configures all components with dependency injection

### Service Layer

- **LLMService (`src/personal_agent/llm/service.py`)** - Manages all LLM operations and response generation
- **MemoryService (`src/personal_agent/memory/service.py`)** - Handles memory operations and conversation history
- **ConversationManager (`src/personal_agent/conversation/manager.py`)** - Manages conversation state and flow

### LLM Integration (`src/personal_agent/llm/`)

- **Providers**: OpenAI and OpenRouter support via provider pattern
- **Rate Limiting**: Built-in rate limiting for API calls
- **Caching**: Response caching to reduce API costs
- **Plugin System**: Extensible client plugin architecture

### Memory System (`src/personal_agent/memory/`)

- **Storage**: SQLite-based persistent storage with async support
- **Models**: Structured memory items with metadata
- **Service**: High-level memory operations and context retrieval

### Conversation System (`src/personal_agent/conversation/`)

- **State Management**: Conversation state tracking
- **Dialogue Acts**: Intent recognition and classification
- **Ambiguity Detection**: Handles unclear user inputs
- **Response Generation**: Context-aware response creation

### Core Systems (`src/personal_agent/core/`)

- **Error Recovery**: Comprehensive error handling and recovery mechanisms
- **Feedback System**: User feedback collection and processing
- **Planning Engine**: Task planning and execution
- **Reasoning Engine**: Decision-making and reasoning capabilities
- **Decision Trees**: Scenario-based decision making

### Configuration (`src/personal_agent/config/`)

- Environment variable-based configuration
- YAML/JSON config file support
- Hierarchical settings with defaults

## Key Architecture Patterns

1. **Service-Oriented Architecture**: Clear separation between services (LLM, Memory, Conversation)
2. **Dependency Injection**: ComponentFactory manages all dependencies and configuration
3. **Plugin System**: Extensible architecture for LLM providers and memory backends
4. **Error Recovery**: Built-in error handling with fallback mechanisms
5. **Async Support**: Async/await patterns throughout for better performance

## Environment Variables

### LLM Configuration
- `PA_LLM__API_KEY`: API key for LLM provider
- `PA_LLM__PROVIDER`: Provider (openrouter, openai)
- `PA_LLM__MODEL`: Model name
- `PA_LLM__TEMPERATURE`: Response temperature (0.0-1.0)
- `PA_LLM__MAX_TOKENS`: Maximum response tokens

### Memory Configuration
- `PA_MEMORY__DATABASE_PATH`: SQLite database path

### Debug Configuration
- `PA_DEBUG`: Enable debug logging

## Testing Strategy

The project uses a comprehensive testing approach:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Custom Test Runner**: `scripts/run_e2e_tests.py` with detailed reporting

Test configurations use pytest fixtures and mock LLM clients for reliable testing without API calls.