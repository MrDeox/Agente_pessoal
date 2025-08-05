"""
pytest configuration and fixtures for Personal Agent tests.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from src.personal_agent.config.settings import Config
from tests.fixtures.mock_llm import create_mock_llm_client, create_test_config


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return create_test_config()


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    return create_mock_llm_client()


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    yield db_path
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_config(temp_db_path):
    """Create a test configuration with temporary database."""
    config = create_test_config()
    config.memory.database_path = temp_db_path
    return config


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Set test environment variables
    original_env = os.environ.copy()
    os.environ["PA_DEBUG"] = "true"
    os.environ["PA_LLM__PROVIDER"] = "mock"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "fixtures" / "data"