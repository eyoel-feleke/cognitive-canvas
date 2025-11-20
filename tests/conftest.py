import sys
from pathlib import Path

# Ensure project root is on sys.path so imports like `from src...` work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# tests/conftest.py
import pytest
from datetime import datetime
from uuid import uuid4
from src.models.content import ContentRecord, ContentMetadata  
from src.models.quiz import Quiz, QuizQuestion, QuizResult  
from src.models.responses import ToolResponse, ErrorResponse, SuccessResponse  

@pytest.fixture
def sample_metadata():
    return ContentMetadata(
        title="Sample Title",
        author="John Doe",
        abstract="A brief summary of the article.",
        keywords=["keyword1", "keyword2"],
        date_published=datetime.now(),
    )

@pytest.fixture
def sample_content_record(sample_metadata):
    return ContentRecord(
        original_content="This is a test content.",
        content_type="text",
        title="Introduction to Testing",
        summary="Short summary",
        category="Education",
        tags=["testing", "sample"],
        embedding=[0.1, 0.2, 0.3],
        timestamp=datetime.now(),
        metadata=sample_metadata
    )
@pytest.fixture
def sample_quiz_question():
    return QuizQuestion(
        number=1,
        topic="Testing",
        question="What is a test?",
        explanation="A test is a procedure to determine the quality of something.",
        choice=["A procedure", "A result", "An error"]
    )
@pytest.fixture
def sample_quiz(sample_quiz_question):
    return Quiz(
        title="Python Basics Quiz",
        quiz_id=uuid4(),
        questions=[sample_quiz_question]  
    )
@pytest.fixture
def sample_quiz_result(sample_quiz):  
    return QuizResult(
        quiz_id=sample_quiz.quiz_id,
        user_name="Test User",
        user_id=uuid4(),
        score=85.0,
        total=10
    )
@pytest.fixture
def sample_tool_response():
    return ToolResponse(
        status="success",
        data={"key": "value"},
        message="Operation completed successfully."
    )
@pytest.fixture
def sample_error_response():
    return ErrorResponse(
        status="error",
        error="An error occurred.",
        details={"code": 500, "info": "Internal Server Error"}
    )
@pytest.fixture
def sample_success_response():
    return SuccessResponse(
        status="success",
        result={"result_key": "result_value"},
        message="Operation was successful."
    )