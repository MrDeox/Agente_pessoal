"""
Test runner for Personal Agent tests.

Provides a simple way to run different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return False


def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    return run_command("python -m pytest tests/unit/ -v")


def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    return run_command("python -m pytest tests/integration/ -v")


def run_e2e_tests():
    """Run end-to-end tests."""
    print("Running end-to-end tests...")
    return run_command("python -m pytest tests/e2e/ -v")


def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    return run_command("python -m pytest tests/ -v")


def run_specific_test(test_path):
    """Run a specific test file or directory."""
    print(f"Running tests in {test_path}...")
    return run_command(f"python -m pytest {test_path} -v")


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Personal Agent Test Runner")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Test suite to run (default: all)"
    )
    parser.add_argument(
        "--specific",
        "-s",
        help="Run specific test file or directory"
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available test files"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    if args.list:
        print("Available test files:")
        test_dir = Path("tests")
        for test_file in test_dir.rglob("test_*.py"):
            print(f"  {test_file}")
        return
    
    if args.specific:
        success = run_specific_test(args.specific)
    elif args.suite == "unit":
        success = run_unit_tests()
    elif args.suite == "integration":
        success = run_integration_tests()
    elif args.suite == "e2e":
        success = run_e2e_tests()
    else:
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()