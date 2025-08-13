"""Tests for data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.content import ContentRecord
from src.models.quiz import QuizQuestion, Quiz, QuizResult
from src.models.responses import ToolResponse, ErrorResponse, SuccessResponse


class TestContentRecord:
    """Test ContentRecord model."""

    def test_content_record_creation(self, sample_content_record):
        """Test creating a valid ContentRecord."""
        assert sample_content_record.id == "test-content-123"
        assert sample_content_record.content_type == "text"
        assert sample_content_record.title == "Introduction to Machine Learning"
        assert len(sample_content_record.tags) == 3
        assert "machine learning" in sample_content_record.tags

    def test_content_record_validation(self):
        """Test ContentRecord validation."""
        # Test missing required fields
        with pytest.raises(ValidationError):
            ContentRecord()

        # Test invalid embedding type
        with pytest.raises(ValidationError):
            ContentRecord(
                id="test",
                original_content="content",
                content_type="text",
                title="title",
                summary="summary",
                category="category",
                tags=["tag1"],
                embedding="not_a_list",  # Should be List[float]
                timestamp=datetime.now()
            )

    def test_content_record_serialization(self, sample_content_record):
        """Test ContentRecord JSON serialization."""
        json_data = sample_content_record.model_dump()
        assert "id" in json_data
        assert "original_content" in json_data
        assert json_data["content_type"] == "text"

        # Test deserialization
        new_record = ContentRecord(**json_data)
        assert new_record.id == sample_content_record.id
        assert new_record.title == sample_content_record.title

    def test_content_record_optional_fields(self):
        """Test ContentRecord with optional fields."""
        record = ContentRecord(
            id="test-id",
            original_content="test content",
            content_type="text",
            title="test title",
            summary="test summary",
            category="test category",
            tags=["tag1", "tag2"],
            embedding=[0.1, 0.2, 0.3],
            timestamp=datetime.now(),
            # source_url and metadata are optional
        )
        assert record.source_url is None
        assert record.metadata == {}


class TestQuizModels:
    """Test Quiz-related models."""

    def test_quiz_question_creation(self):
        """Test creating a QuizQuestion."""
        question = QuizQuestion(
            question="What is AI?",
            explanation="AI stands for Artificial Intelligence."
        )
        assert question.question == "What is AI?"
        assert "Artificial Intelligence" in question.explanation

    def test_quiz_creation(self, sample_quiz):
        """Test creating a Quiz."""
        assert sample_quiz.title == "Machine Learning Basics"
        assert len(sample_quiz.questions) == 2
        assert isinstance(sample_quiz.questions[0], QuizQuestion)

    def test_quiz_result_creation(self):
        """Test creating a QuizResult."""
        result = QuizResult(
            quiz_id="quiz-123",
            user_id="user-456",
            score=8,
            total=10
        )
        assert result.score == 8
        assert result.total == 10
        assert result.quiz_id == "quiz-123"

    def test_quiz_validation(self):
        """Test Quiz model validation."""
        # Test empty questions list
        quiz = Quiz(title="Empty Quiz", questions=[])
        assert len(quiz.questions) == 0

        # Test invalid score in QuizResult
        with pytest.raises(ValidationError):
            QuizResult(
                quiz_id="quiz-123",
                user_id="user-456",
                score="not_a_number",  # Should be int
                total=10
            )


class TestResponseModels:
    """Test response models."""

    def test_tool_response_creation(self, sample_tool_response):
        """Test creating a ToolResponse."""
        assert sample_tool_response.status == "success"
        assert sample_tool_response.data["content_id"] == "test-123"
        assert "successfully" in sample_tool_response.message

    def test_error_response_creation(self):
        """Test creating an ErrorResponse."""
        error = ErrorResponse(
            error="Validation failed",
            details={"field": "title", "issue": "required"}
        )
        assert error.error == "Validation failed"
        assert error.details["field"] == "title"

    def test_success_response_creation(self):
        """Test creating a SuccessResponse."""
        success = SuccessResponse(
            result={"id": "123", "status": "created"},
            message="Operation completed successfully"
        )
        assert success.result["id"] == "123"
        assert "completed" in success.message

    def test_response_serialization(self):
        """Test response model serialization."""
        tool_response = ToolResponse(
            status="error",
            message="Something went wrong"
        )
        json_data = tool_response.model_dump()
        assert json_data["status"] == "error"
        assert json_data["data"] is None
        assert json_data["message"] == "Something went wrong"

    def test_response_optional_fields(self):
        """Test response models with optional fields."""
        # ToolResponse with minimal fields
        minimal_response = ToolResponse(status="pending")
        assert minimal_response.data is None
        assert minimal_response.message is None

        # ErrorResponse with minimal fields
        minimal_error = ErrorResponse(error="Unknown error")
        assert minimal_error.details is None