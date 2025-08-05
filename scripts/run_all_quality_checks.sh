#!/bin/bash

# Script to run all code quality checks

# Exit on any error
set -e

# Function to check if a Python package is installed
check_package() {
    python3 -c "import $1" 2>/dev/null
}

# Function to install a Python package
install_package() {
    local package=$1
    echo "Installing $package..."
    pip install $package
}

# Check and install required packages
echo "Checking required packages..."
REQUIRED_PACKAGES=("PyYAML" "cryptography" "openai" "flake8")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package%%=*}" 2>/dev/null; then
        echo "$package not found, installing..."
        install_package "$package"
    fi
done

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Function to run a check and handle errors
run_check() {
    local check_name=$1
    local check_command=$2
    
    echo "Running $check_name..."
    if eval $check_command; then
        echo "$check_name passed!"
    else
        echo "$check_name failed!"
        exit 1
    fi
}

# Run flake8
run_check "flake8" "flake8 src/"

# Run our docstring check
run_check "docstring check" "python3 tests/integration/utils/test_docstrings.py"

# Run our common utilities test
run_check "common utilities test" "python3 tests/integration/utils/test_common_utils.py"

# Run our dependency injection test
run_check "dependency injection test" "python3 tests/integration/core/test_dependency_injection.py"

# Run our configuration test
run_check "configuration test" "python3 tests/unit/config/test_config.py"

echo "All quality checks passed!"