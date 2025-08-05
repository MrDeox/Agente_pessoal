#!/bin/bash

# Script to run code quality checks

# Activate virtual environment
source venv/bin/activate

# Run flake8
echo "Running flake8..."
flake8 src/
if [ $? -eq 0 ]; then
    echo "flake8 checks passed!"
else
    echo "flake8 checks failed!"
    exit 1
fi

# Run other quality checks here if needed
# For example, you could add pylint, mypy, or other tools

echo "All code quality checks passed!"