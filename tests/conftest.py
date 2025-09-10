"""
Pytest configuration and fixtures for JarvisX tests
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for testing"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    mock = Mock()
    mock.generate.return_value = "Mock response"
    mock.stream_generate.return_value = ["Mock", " response"]
    return mock

@pytest.fixture
def mock_memory():
    """Mock memory system for testing"""
    mock = Mock()
    mock.get_profile.return_value = {"id": "test", "name": "Test User"}
    mock.save_conversation.return_value = "conv_123"
    mock.save_message.return_value = "msg_123"
    return mock

@pytest.fixture
def mock_permissions():
    """Mock permissions system for testing"""
    mock = Mock()
    mock.check_permission.return_value = True
    mock.get_policy.return_value = "ask-every-time"
    return mock

@pytest.fixture
def sample_context():
    """Sample context for testing"""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "conversation_id": "test_conv",
        "permissions": ["FILE_READ", "FILE_WRITE"]
    }