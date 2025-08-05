# Personal Agent with LLM Integration

A personal AI assistant with memory capabilities and LLM integration.

## Features

- Conversational AI assistant
- Persistent memory storage
- LLM integration (OpenAI GPT models)
- Configurable settings
- Extensible architecture

## Requirements

- Python 3.8+
- OpenAI API key (for LLM features)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd personal-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The personal agent can be configured through environment variables:

### LLM Configuration

- `PA_LLM__API_KEY`: Your API key for the LLM provider (required for LLM features)
- `PA_LLM__PROVIDER`: LLM provider (default: "openrouter")
- `PA_LLM__MODEL`: Model to use (default: "qwen/qwen3-coder:free")
- `PA_LLM__TEMPERATURE`: Temperature for response generation (default: 0.7)
- `PA_LLM__MAX_TOKENS`: Maximum tokens in response (default: 1000)

### Memory Configuration

- `PA_MEMORY__DATABASE_PATH`: Path to memory database (default: "data/memory.db")

### Debug Configuration

- `PA_DEBUG`: Enable debug mode (default: false)

## Usage

### Running the Agent

To run the interactive agent:

```bash
python scripts/run_agent.py
```

Before running, set your API key. For OpenRouter (default):

```bash
export PA_LLM__API_KEY="your-openrouter-api-key"
```

Or for OpenAI:

```bash
export PA_LLM__PROVIDER="openai"
export PA_LLM__API_KEY="your-openai-api-key"
```

Alternatively, you can use the provided script for OpenRouter:

```bash
export PA_LLM__API_KEY="your-openrouter-api-key"
./scripts/run_agent_openrouter.sh
```

### Testing LLM Integration

To test the LLM integration:

```bash
python scripts/test_llm.py
```

To specifically test OpenRouter integration:

```bash
python scripts/test_openrouter.py
```

## Project Structure

```
personal-agent/
├── src/
│   └── personal_agent/
│       ├── config/          # Configuration management
│       ├── core/            # Core agent functionality
│       ├── llm/             # LLM integration
│       ├── memory/          # Memory storage and management
│       └── utils/           # Utility functions
├── scripts/                 # Executable scripts
├── data/                    # Data storage
├── tests/                   # Automated tests
│   └── e2e/                 # End-to-end tests
└── docs/                    # Documentation
```

## LLM Integration

The agent supports multiple LLM providers including OpenAI and OpenRouter. By default, it uses OpenRouter with the Qwen3 Coder model.

### Using OpenRouter (Default - Free Option Available)

1. Obtain an API key from [OpenRouter](https://openrouter.ai/)
2. Set the `PA_LLM__API_KEY` environment variable
3. Run the agent

### Using OpenAI (Alternative)

1. Obtain an API key from [OpenAI](https://platform.openai.com/)
2. Set the following environment variables:
   ```bash
   export PA_LLM__PROVIDER="openai"
   export PA_LLM__API_KEY="your-openai-api-key"
   export PA_LLM__MODEL="gpt-4"  # or gpt-3.5-turbo, etc.
   ```

The agent will automatically use conversation history and memory context to generate more informed responses.

## Memory System

The agent has a persistent memory system that stores:
- Conversation history
- User preferences
- Important facts

Memory is stored in a SQLite database by default.

## Extending the Agent

The agent is designed to be extensible. You can add:
- New LLM providers
- Additional tools and capabilities
- Custom memory storage backends
- New configuration options

## Development

### Running Tests

#### Unit/Integration Tests
```bash
python scripts/test_memory.py
python scripts/test_agent_memory.py
python scripts/test_llm.py
```

#### End-to-End Tests
```bash
# Run all end-to-end tests
python3 scripts/run_e2e_tests.py

# Run specific test suites
python3 scripts/run_e2e_tests.py --suites conversation_flow memory_functionality

# List available test suites
python3 scripts/run_e2e_tests.py --list-suites
```

See `tests/README.md` for detailed documentation on end-to-end tests.

### Code Structure

- `src/personal_agent/core/agent.py`: Main agent logic
- `src/personal_agent/memory/`: Memory storage implementation
- `src/personal_agent/llm/`: LLM integration
- `src/personal_agent/config/`: Configuration management

## License

This project is licensed under the MIT License.