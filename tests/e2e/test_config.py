#!/usr/bin/env python3
"""
Configuration for end-to-end tests.

This module provides configurable test scenarios and settings.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class TestScenario:
    """Represents a test scenario configuration."""
    name: str
    description: str
    enabled: bool = True
    timeout: int = 30  # seconds
    require_llm: bool = False
    require_api_key: bool = False
    test_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestConfig:
    """Main test configuration."""
    # Test environment settings
    test_user_id: str = "e2e_test_user"
    test_database_path: str = "data/test_memory.db"
    cleanup_after_test: bool = True
    
    # LLM settings
    test_llm_provider: str = "mock"  # or "openai", "openrouter"
    test_llm_model: str = "gpt-3.5-turbo"
    test_llm_timeout: int = 30
    
    # Test scenarios
    scenarios: List[TestScenario] = field(default_factory=list)
    
    # Reporting settings
    generate_html_report: bool = True
    save_detailed_logs: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default scenarios if none provided."""
        if not self.scenarios:
            self.scenarios = self._get_default_scenarios()
    
    def _get_default_scenarios(self) -> List[TestScenario]:
        """Get default test scenarios."""
        return [
            TestScenario(
                name="basic_conversation",
                description="Test basic conversation flow",
                enabled=True,
                timeout=15,
                require_llm=False,
                require_api_key=False
            ),
            TestScenario(
                name="memory_persistence",
                description="Test memory storage and retrieval",
                enabled=True,
                timeout=20,
                require_llm=False,
                require_api_key=False
            ),
            TestScenario(
                name="llm_integration",
                description="Test LLM integration with context",
                enabled=True,
                timeout=30,
                require_llm=True,
                require_api_key=True
            ),
            TestScenario(
                name="feedback_collection",
                description="Test feedback collection and processing",
                enabled=True,
                timeout=15,
                require_llm=False,
                require_api_key=False
            ),
            TestScenario(
                name="error_handling",
                description="Test error handling and edge cases",
                enabled=True,
                timeout=20,
                require_llm=False,
                require_api_key=False
            ),
            TestScenario(
                name="long_conversation",
                description="Test long conversation flow",
                enabled=False,  # Disabled by default
                timeout=60,
                require_llm=True,
                require_api_key=True
            )
        ]
    
    def get_enabled_scenarios(self) -> List[TestScenario]:
        """Get list of enabled scenarios."""
        return [scenario for scenario in self.scenarios if scenario.enabled]
    
    def get_scenario(self, name: str) -> TestScenario:
        """Get a specific scenario by name."""
        for scenario in self.scenarios:
            if scenario.name == name:
                return scenario
        raise ValueError(f"Scenario '{name}' not found")
    
    @classmethod
    def load_from_env(cls) -> 'TestConfig':
        """Load configuration from environment variables."""
        config = cls()
        
        # Load from environment variables
        if os.getenv("PA_TEST_USER_ID"):
            config.test_user_id = os.getenv("PA_TEST_USER_ID")
        
        if os.getenv("PA_TEST_DATABASE_PATH"):
            config.test_database_path = os.getenv("PA_TEST_DATABASE_PATH")
        
        if os.getenv("PA_TEST_CLEANUP"):
            config.cleanup_after_test = os.getenv("PA_TEST_CLEANUP").lower() in ["true", "1", "yes"]
        
        if os.getenv("PA_TEST_LLM_PROVIDER"):
            config.test_llm_provider = os.getenv("PA_TEST_LLM_PROVIDER")
        
        if os.getenv("PA_TEST_LLM_MODEL"):
            config.test_llm_model = os.getenv("PA_TEST_LLM_MODEL")
        
        if os.getenv("PA_TEST_LLM_TIMEOUT"):
            config.test_llm_timeout = int(os.getenv("PA_TEST_LLM_TIMEOUT"))
        
        if os.getenv("PA_TEST_GENERATE_HTML_REPORT"):
            config.generate_html_report = os.getenv("PA_TEST_GENERATE_HTML_REPORT").lower() in ["true", "1", "yes"]
        
        if os.getenv("PA_TEST_SAVE_DETAILED_LOGS"):
            config.save_detailed_logs = os.getenv("PA_TEST_SAVE_DETAILED_LOGS").lower() in ["true", "1", "yes"]
        
        if os.getenv("PA_TEST_LOG_LEVEL"):
            config.log_level = os.getenv("PA_TEST_LOG_LEVEL")
        
        return config


# Predefined test scenarios for common use cases
PREDEFINED_SCENARIOS = {
    "smoke_test": [
        "basic_conversation",
        "memory_persistence"
    ],
    "full_test": [
        "basic_conversation",
        "memory_persistence",
        "llm_integration",
        "feedback_collection",
        "error_handling"
    ],
    "llm_test": [
        "llm_integration",
        "long_conversation"
    ],
    "stress_test": [
        "long_conversation",
        "error_handling"
    ]
}


def get_test_config(scenario_set: str = "full_test") -> TestConfig:
    """Get test configuration for a specific scenario set."""
    config = TestConfig.load_from_env()
    
    # Enable only the scenarios in the specified set
    if scenario_set in PREDEFINED_SCENARIOS:
        enabled_scenarios = PREDEFINED_SCENARIOS[scenario_set]
        for scenario in config.scenarios:
            scenario.enabled = scenario.name in enabled_scenarios
    
    return config


# Example test data for scenarios
TEST_CONVERSATIONS = {
    "greeting": [
        {"user": "Hello!", "expected_keywords": ["hello", "hi", "welcome"]},
        {"user": "How are you?", "expected_keywords": ["well", "good", "fine", "assistant"]}
    ],
    "memory_test": [
        {"user": "My favorite color is blue.", "remember": "fact"},
        {"user": "I prefer Python programming.", "remember": "preference"},
        {"user": "What is my favorite color?", "expected_keywords": ["blue"]},
        {"user": "What programming language do I prefer?", "expected_keywords": ["python"]}
    ],
    "feedback_test": [
        {"user": "Tell me a joke.", "collect_feedback": True, "rating": 4},
        {"user": "What's the weather like?", "collect_feedback": True, "rating": 2}
    ]
}


def main():
    """Main function for testing the configuration."""
    print("Test configuration module loaded successfully")
    
    # Load default configuration
    config = TestConfig()
    print(f"Default config loaded with {len(config.scenarios)} scenarios")
    
    # Load from environment
    env_config = TestConfig.load_from_env()
    print(f"Environment config loaded with {len(env_config.get_enabled_scenarios())} enabled scenarios")
    
    # Test predefined scenario sets
    for scenario_set in PREDEFINED_SCENARIOS:
        set_config = get_test_config(scenario_set)
        enabled = len(set_config.get_enabled_scenarios())
        print(f"Scenario set '{scenario_set}' has {enabled} enabled scenarios")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())