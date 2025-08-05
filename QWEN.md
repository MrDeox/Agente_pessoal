# Qwen Codebase Guidelines

## Build/Lint/Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all tests
python scripts/test_agent_llm.py
python scripts/test_llm.py
python scripts/test_feedback.py
python scripts/test_openrouter.py

# Run a single test
python scripts/test_llm.py  # Example for LLM tests
```

### Linting
```bash
# No specific linter configured, but follow PEP 8
# Consider using flake8 or pylint for linting
```

## Code Style Guidelines

### Imports
- Use absolute imports when possible
- Group imports in standard order: standard library, third-party, local
- Avoid wildcard imports

### Formatting
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Limit lines to 88 characters (recommended)
- Use blank lines to separate logical sections

### Types
- Use type hints for function parameters and return values
- Use `Optional[T]` for parameters that can be None
- Use `List`, `Dict`, etc. from typing module

### Naming Conventions
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
- Use descriptive names that convey purpose

### Error Handling
- Use specific exception types when possible
- Log errors appropriately
- Provide meaningful error messages
- Use try/except blocks for expected exceptions

### Documentation
- Use docstrings for all public classes and functions
- Follow Google Python Style Guide for docstrings
- Include type information in docstrings
- Add comments for complex logic

### Additional Notes
- Add the src directory to Python path when running scripts
- Use environment variables for configuration
- Follow existing patterns in the codebase