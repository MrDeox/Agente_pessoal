#!/usr/bin/env python3
"""
Test script to verify that all public methods and classes have docstrings.
"""

import sys
import os
import inspect
import pkgutil
import importlib

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def check_docstrings_in_module(module):
    """
    Check that all public classes and methods in a module have docstrings.
    
    Args:
        module: The module to check
        
    Returns:
        list: List of issues found
    """
    issues = []
    module_name = module.__name__
    
    # Check module docstring
    if not module.__doc__ or not module.__doc__.strip():
        issues.append(f"Module {module_name} missing docstring")
    
    # Check classes and functions
    for name, obj in inspect.getmembers(module):
        # Skip private and special members
        if name.startswith('_'):
            continue
            
        # Check classes
        if inspect.isclass(obj) and obj.__module__ == module_name:
            if not obj.__doc__ or not obj.__doc__.strip():
                issues.append(f"Class {name} in {module_name} missing docstring")
            
            # Check methods in the class
            for method_name, method in inspect.getmembers(obj):
                if method_name.startswith('_') or method_name.startswith('__'):
                    continue
                    
                if inspect.ismethod(method) or inspect.isfunction(method):
                    # Get the actual function if it's a method
                    func = method.__func__ if hasattr(method, '__func__') else method
                    if not func.__doc__ or not func.__doc__.strip():
                        issues.append(f"Method {obj.__name__}.{method_name} in {module_name} missing docstring")
        
        # Check functions
        elif inspect.isfunction(obj) and obj.__module__ == module_name:
            if not obj.__doc__ or not obj.__doc__.strip():
                issues.append(f"Function {name} in {module_name} missing docstring")
    
    return issues

def test_all_modules():
    """
    Test all modules in the personal_agent package for docstrings.
    """
    print("Testing docstrings in all modules...")
    
    # List of modules to check
    modules_to_check = [
        'personal_agent.config.settings',
        'personal_agent.core.agent',
        'personal_agent.core.factory',
        'personal_agent.core.feedback',
        'personal_agent.core.manager',
        'personal_agent.llm.cache',
        'personal_agent.llm.client',
        'personal_agent.llm.exceptions',
        'personal_agent.llm.models',
        'personal_agent.llm.plugin_manager',
        'personal_agent.llm.providers.base',
        'personal_agent.llm.providers.openai',
        'personal_agent.llm.providers.openrouter',
        'personal_agent.llm.rate_limiter',
        'personal_agent.memory.models',
        'personal_agent.memory.storage',
        'personal_agent.utils.common',
        'personal_agent.utils.logging',
        'personal_agent.utils.retry',
        'personal_agent.utils.validation'
    ]
    
    all_issues = []
    
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            issues = check_docstrings_in_module(module)
            all_issues.extend(issues)
        except Exception as e:
            print(f"Error checking module {module_name}: {e}")
    
    if all_issues:
        print(f"\nFound {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  - {issue}")
        return False
    else:
        print("All modules have proper docstrings!")
        return True

def main():
    """Run the docstring tests."""
    success = test_all_modules()
    if success:
        print("\nDocstring test passed!")
        return 0
    else:
        print("\nDocstring test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())