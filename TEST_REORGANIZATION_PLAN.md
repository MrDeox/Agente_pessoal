# Test Reorganization Plan - Personal Agent

## Current Issues Identified

### 1. **Critical Issues**
- **Import path inconsistencies**: Tests using `personal_agent` vs `src.personal_agent`
- **Missing storage plugin**: Factory expects `memory/sqlite.py` but storage is in `memory/storage.py`
- **API key dependencies**: Tests fail without API keys, need proper mocking
- **Duplicate tests**: 25 script tests overlap with 11 proper tests

### 2. **Architecture Misalignment** 
- Tests not updated for refactored storage.py
- Tests not using new constants module
- Tests not using new error handling patterns
- Factory plugin system broken after refactoring

### 3. **Organization Problems**
- Tests scattered between `scripts/` and `tests/` directories
- Inconsistent naming conventions
- No clear separation of unit vs integration vs e2e tests

## Proposed New Structure

```
tests/
├── unit/                          # Unit tests for individual modules
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── test_settings.py       # From scripts/test_config.py
│   │   └── test_constants.py      # New - test constants module
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── test_validation.py     # From scripts/test_validation.py
│   │   ├── test_common_utils.py   # From scripts/test_common_utils.py
│   │   ├── test_retry.py          # From scripts/test_retry.py
│   │   ├── test_logging.py        # From scripts/test_logging.py
│   │   └── test_error_handling.py # New - test error handling
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── test_storage.py        # From scripts/test_basic_memory.py
│   │   ├── test_models.py         # New
│   │   └── test_service.py        # New
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_client.py         # From scripts/test_llm.py
│   │   ├── test_providers.py      # From scripts/test_openrouter.py
│   │   ├── test_cache.py          # From scripts/test_llm_cache.py
│   │   └── test_plugin_system.py  # From scripts/test_plugin_system.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_agent.py          # Core agent unit tests
│   │   ├── test_factory.py        # Component factory tests
│   │   ├── test_reasoning.py      # From scripts/test_advanced_reasoning.py
│   │   └── test_feedback.py       # From scripts/test_feedback.py
│   └── conversation/
│       ├── __init__.py
│       ├── test_manager.py        # From scripts/test_conversation_flow.py
│       └── test_ambiguity.py      # From tests/test_ambiguity_handling.py
├── integration/                   # Integration tests
│   ├── __init__.py
│   ├── test_agent_integration.py  # From scripts/test_refactored_agent.py
│   ├── test_memory_integration.py # From scripts/test_knowledge_memory.py
│   └── test_llm_integration.py    # From scripts/test_agent_llm.py
├── e2e/                          # End-to-end tests (keep existing structure)
│   ├── __init__.py
│   ├── test_conversation_flow.py
│   ├── test_memory_functionality.py
│   ├── test_llm_integration.py
│   ├── test_feedback_mechanism.py
│   ├── test_error_handling.py
│   ├── test_config.py
│   └── test_report_generator.py
├── fixtures/                     # Test data and fixtures
│   ├── __init__.py
│   ├── mock_llm.py              # Mock LLM for testing without API keys
│   ├── test_data.py             # Common test data
│   └── test_config.py           # Test configuration
├── conftest.py                  # pytest configuration
└── __init__.py
```

## Key Changes

### 1. **Consolidate Tests**
- Move all `scripts/test_*.py` to appropriate `tests/` subdirectories
- Remove duplicate functionality
- Standardize naming: `test_<module>.py`

### 2. **Fix Architecture Issues**
- Update imports to use `src.personal_agent`
- Create mock LLM client for tests without API keys
- Fix storage plugin system
- Update tests to use new constants and error handling

### 3. **Create Test Infrastructure**
- `conftest.py` with pytest fixtures
- Mock LLM client for testing without API keys
- Test configuration management
- Standardized test utilities

### 4. **Update Failing Tests**
- Fix import paths in all test files
- Update factory to recognize refactored storage
- Add proper mocking for external dependencies
- Update tests to use new architecture patterns

## Implementation Steps

1. **Create new test structure** with proper directories
2. **Move and rename test files** according to new organization
3. **Fix import paths** throughout all tests
4. **Create test infrastructure** (mocks, fixtures, configuration)
5. **Update failing tests** to work with refactored architecture
6. **Create test runner** script for running all tests
7. **Verify all tests pass** and provide good coverage

## Priority Order
1. **High**: Fix critical failing tests, update import paths
2. **High**: Create mock infrastructure for LLM testing
3. **Medium**: Reorganize file structure 
4. **Low**: Add missing unit tests for new modules