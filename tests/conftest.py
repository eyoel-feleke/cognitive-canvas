"""Test configuration and fixtures for ContentGraph MCP tests."""

import pytest
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from src.models.content import ContentRecord
from src.models.quiz import QuizQuestion, Quiz
from src.models.responses import ToolResponse, ErrorResponse, SuccessResponse


@pytest.fixture
def sample_content_record() -> ContentRecord:
    """Create a sample ContentRecord for testing."""
    return ContentRecord(
        id="test-content-123",
        original_content="This is a sample article about machine learning and AI.",
        content_type="text",
        title="Introduction to Machine Learning",
        summary="A brief overview of machine learning concepts and applications.",
        category="Technology",
        tags=["machine learning", "AI", "technology"],
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5] * 20,  # Mock 100-dimensional embedding
        timestamp=datetime.now(),
        source_url="https://example.com/ml-intro",
        metadata={"author": "Test Author", "word_count": 150}
    )


@pytest.fixture
def sample_quiz_questions() -> List[QuizQuestion]:
    """Create sample quiz questions for testing."""
    return [
        QuizQuestion(
            question="What is machine learning?",
            explanation="Machine learning is a subset of AI that enables computers to learn without explicit programming."
        ),
        QuizQuestion(
            question="What are the main types of machine learning?",
            explanation="The main types are supervised, unsupervised, and reinforcement learning."
        )
    ]


@pytest.fixture
def sample_quiz(sample_quiz_questions) -> Quiz:
    """Create a sample quiz for testing."""
    return Quiz(
        title="Machine Learning Basics",
        questions=sample_quiz_questions
    )


@pytest.fixture
def sample_url_content() -> Dict[str, Any]:
    """Sample web content for testing content extraction."""
    return {
        "url": "https://example.com/test-article",
        "html": """<html>
            <head><title>Test Article</title></head>
            <body>
                <h1>Test Article Title</h1>
                <p>This is the main content of the test article.</p>
                <p>It contains multiple paragraphs with useful information.</p>
            </body>
        </html>""",
        "expected_title": "Test Article Title",
        "expected_content": "This is the main content of the test article. It contains multiple paragraphs with useful information."
    }


@pytest.fixture
def mock_openai_response() -> Dict[str, Any]:
    """Mock OpenAI API response for testing."""
    return {
        "choices": [{
            "message": {
                "content": '{"category": "Technology", "tags": ["AI", "testing"], "summary": "Test summary"}'
            }
        }]
    }


@pytest.fixture
def mock_embedding() -> List[float]:
    """Mock embedding vector for testing."""
    return [0.1] * 384  # Typical dimension for all-MiniLM-L6-v2


@pytest.fixture
def temp_chroma_db():
    """Create a temporary ChromaDB instance for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for testing web content extraction."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<html>
            <head><title>Test Page</title></head>
            <body><h1>Test Title</h1><p>Test content</p></body>
        </html>"""
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer model for testing."""
    with patch('sentence_transformers.SentenceTransformer') as mock_model:
        mock_instance = Mock()
        mock_instance.encode.return_value = [0.1] * 384
        mock_model.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = '{"category": "Technology", "summary": "Test summary", "tags": ["test"]}'
        mock_instance.chat.completions.create.return_value = mock_completion
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    os.environ.setdefault('CHROMA_DB_PATH', './test_chroma_db')
    yield
    # Cleanup if needed
    if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY'] == 'test-key':
        del os.environ['OPENAI_API_KEY']


@pytest.fixture
def sample_tool_response() -> ToolResponse:
    """Create a sample tool response for testing."""
    return ToolResponse(
        status="success",
        data={"content_id": "test-123", "category": "Technology"},
        message="Content stored successfully"
    )
