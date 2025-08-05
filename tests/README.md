# Personal Agent - End-to-End Tests

This directory contains comprehensive end-to-end tests for the Personal Agent project.

## Test Structure

```
tests/
├── e2e/                    # End-to-end tests
│   ├── __init__.py
│   ├── test_conversation_flow.py     # Comprehensive conversation flow tests
│   ├── test_memory_functionality.py  # Memory storage and retrieval tests
│   ├── test_llm_integration.py       # LLM integration and context tests
│   ├── test_feedback_mechanism.py    # Feedback collection and processing tests
│   ├── test_error_handling.py        # Error handling and edge cases tests
│   ├── test_config.py                # Test configuration and scenarios
│   └── test_report_generator.py      # Unified test report generation
└── __init__.py
```

## Test Suites

### 1. Conversation Flow Tests (`test_conversation_flow.py`)
- Basic conversation functionality
- Welcome messages and exit commands
- Conversation history management
- Integration of all core components

### 2. Memory Functionality Tests (`test_memory_functionality.py`)
- Memory storage operations (save, retrieve, update, delete)
- Conversation history persistence
- Knowledge storage (preferences and facts)
- Memory search and retrieval
- Memory persistence across sessions

### 3. LLM Integration Tests (`test_llm_integration.py`)
- LLM client initialization
- Response generation with context
- Multi-turn conversation flows
- Error handling and fallbacks
- Message formatting and structure

### 4. Feedback Mechanism Tests (`test_feedback_mechanism.py`)
- Rating feedback collection
- Thumbs up/down feedback collection
- Feedback storage and retrieval
- Feedback statistics calculation
- Response adaptation based on feedback

### 5. Error Handling Tests (`test_error_handling.py`)
- Input validation and edge cases
- Memory error handling
- LLM error handling and fallbacks
- Exit command processing
- Boundary condition testing
- Exception handling and recovery

## Running Tests

### Run All Tests

```bash
python scripts/run_e2e_tests.py
```

### Run Specific Test Suites

```bash
# List available test suites
python scripts/run_e2e_tests.py --list-suites

# Run specific suites
python scripts/run_e2e_tests.py --suites conversation_flow memory_functionality

# Run individual test suite
python tests/e2e/test_conversation_flow.py
```

## Test Configuration

Tests can be configured using environment variables:

- `PA_TEST_USER_ID` - Test user ID (default: "e2e_test_user")
- `PA_TEST_DATABASE_PATH` - Test database path (default: "data/test_memory.db")
- `PA_TEST_LLM_PROVIDER` - LLM provider for tests (default: "mock")
- `PA_TEST_CLEANUP` - Cleanup test data after run (default: "true")

## Test Reports

Test results are saved in the `test_reports/` directory:

- Individual test suite reports
- Unified text and JSON reports
- Detailed failure information
- Performance metrics

## Development

To add new test suites:

1. Create a new test file in `tests/e2e/`
2. Follow the existing pattern for test results and reporting
3. Add the suite to the test runner in `scripts/run_e2e_tests.py`
4. Update this README with suite documentation