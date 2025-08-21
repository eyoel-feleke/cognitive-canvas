from datetime import datetime
import uuid
from src.models.content import ContentMetadata, ContentRecord
from src.models.quiz import Quiz, QuizQuestion, QuizResult
from src.models.responses import ErrorResponse, SuccessResponse, ToolResponse
import pytest
from pydantic import ValidationError

class TestContentRecordAndMetadata:
    """Test ContentMetadata Model."""
    def test_content_metadata(self, sample_metadata):
        """Test the ContentMetadata model."""
        assert sample_metadata.title =="Sample Title", f"Expected 'Sample Title', got {sample_metadata.title}"
        assert sample_metadata.author == "John Doe", f"Expected 'John Doe', got {sample_metadata.author}"
        assert sample_metadata.abstract == "A brief summary of the article.", f"Expected 'A brief summary of the article.', got {sample_metadata.abstract}"
        assert sample_metadata.keywords == ["keyword1", "keyword2"], f"Expected ['keyword1', 'keyword2'], got {sample_metadata.keywords}"
        assert isinstance(sample_metadata.date_published, datetime), f"Expected date_published to be datetime instance, but got {type(sample_metadata.date_published)}"
        
    def test_content_metadata_validation(self):
        """Test the ContentMetadata model validation."""
        with pytest.raises(ValidationError):
            ContentMetadata()
            
        with pytest.raises(ValidationError):
            ContentMetadata(
                title="sample",
                author="John Doe",
                abstract="This is a sample abstract.",
                keywords="not a list",
                citation="Sample Citation"
            )
    def test_content_metadata_serialization(self, sample_metadata):
        """Test ContentMetadata JSON serialization and deserialization."""
        json_data = sample_metadata.model_dump()
        assert "meta_id" in json_data, f"Expected 'meta_id' in JSON data, got {json_data}"
        assert "title" in json_data, f"Expected 'title' in JSON data, got {json_data}"
        
        
        new_metadata = ContentMetadata(**json_data)
        assert new_metadata.title == sample_metadata.title
        assert new_metadata.abstract == sample_metadata.abstract
        
    def test_content_metadata_optional_fields(self):
        """Test ContentMetadata with optional fields."""
        metadata = ContentMetadata(
            title = "Sample Metadata", 
            author="Author Name",
            abstract="This is a synopsis of the sample metadata.",
            keywords=["keyword1", "testing error"],
            date_published=datetime.now(),
            citation="Citation Example" 
        )
        assert metadata.keywords == ["keyword1", "keyword2"], f"Expected ['keyword1', 'keyword2'], got {metadata.keywords}" # This will fail to show the error message is working
        assert metadata.citation == "Citation Example", f"Expected 'Citation Example', got {metadata.citation}"
    
    def test_content_record(self, sample_content_record):
        """Test the ContentRecord model."""
        assert sample_content_record.original_content == "This is a test content.", f"Expected 'This is a test content., got{sample_content_record.original_content}"
        assert sample_content_record.content_type == "text", f"Expected 'text', got {sample_content_record.content_type}"
        assert sample_content_record.title == "Introduction to Testing", f"Expected 'Introduction to Testing', got {sample_content_record.title}"
        assert sample_content_record.summary == "Short summary", f"Expected 'Short summary', got {sample_content_record.summary}"
        assert sample_content_record.category == "Education", f"Expected 'Education', got {sample_content_record.category}"
        assert sample_content_record.tags == ["testing", "sample"], f"Expected ['testing', 'sample'], got {sample_content_record.tags}"
        assert isinstance(sample_content_record.timestamp, datetime), f"Expected timestamp as datetime instance, but got {type(sample_content_record.timestamp)}"
        assert isinstance(sample_content_record.metadata, ContentMetadata), f"Expected metadata to be an instance of ContentMetadata, but got {sample_content_record.metadata}"
        
    def test_content_record_validation(self):
        """Test the ContentRecord model validation."""
        with pytest.raises(ValidationError):
            ContentRecord()

        
        with pytest.raises(ValidationError):
            ContentRecord(
                original_content="This is a test content.",
                content_type="text",
                title="Introduction to Testing",
                summary="Short summary",
                category="Education",
                tags=["testing", "sample"],
                embedding="not_a_list",  
                timestamp=datetime.now(),
            )
    def test_content_record_serialization(self, sample_content_record):
        """Test ContentRecord JSON serialization and deserialization."""
        json_data = sample_content_record.model_dump()
        assert "content_id" in json_data, f"Expected 'content_id' in JSON data, got {json_data}"
        assert "original_content" in json_data, f"Expected 'original_content' in JSON data, got {json_data}"
        
        
        new_record = ContentRecord(**json_data)
        assert new_record.original_content == sample_content_record.original_content,f"Expected 'This is a test content.', got {new_record.original_content}"
        assert new_record.title == sample_content_record.title, f"Expected 'Introduction to Testing', got {new_record.title}"
    def test_content_record_optional_fields(self):
        """Test ContentRecord with optional fields."""
        metadata = ContentMetadata(
            title = "Sample Metadata", 
            author="Author Name",
            abstract="This is a synopsis of the sample metadata.",
            keywords=["keyword1", "keyword2"],
            date_published=datetime.now(),
            citation="Citation Example" 
        )
        record = ContentRecord(
            original_content="text",
            content_type="text",
            title="title",
            summary="summary",
            category="cat",
            tags=["tag"],
            embedding=[0.1, 0.2],
            timestamp=datetime.now(),
            metadata=metadata
        )
        assert record.source_url is None
        assert isinstance(record.metadata, ContentMetadata)

class TestQuizModels:
    """Test Quiz, QuizQuestion, and QuizResult Models."""
        
    def test_quiz_question_creation(self, sample_quiz_question):
        """Testing Quiz question Creation"""
        question = QuizQuestion(
            number=1,
            topic="Python",
            question="What is the output of print(2 ** 3)?",
            explanation="2 raised to the power of 3 equals 8.",
            choice=["6", "7", "8", "9"]
        )
        assert question.number == 1, f"Expected int got {type(question.number)}"
        assert question.topic == "Python", f"Expected 'Python', got {question.topic}"
        assert question.question == "What is the output of print(2 ** 3)?", f"Expected 'What is the output of print(2 ** 3)?', got {question.question}"
        assert question.explanation == "2 raised to the power of 3 equals 8.", f"Expected '2 raised to the power of 3 equals 8.', got {question.explanation}"
        assert question.choice == ["6", "7", "8", "9"], f"Expected ['6','7','8','9'], got {question.choice}"
    def test_quiz_creation(self, sample_quiz):
        """Testing Quiz Creation"""
        assert sample_quiz.title == "Python Basics Quiz", f"Expected 'Python Basics Quiz', got {sample_quiz.title}"
        assert sample_quiz.quiz_id is not None, f"Expected quiz_id to not be None, got {sample_quiz.quiz_id}"
        assert len(sample_quiz.questions) == 1, f"Expected 1, got {len(sample_quiz.questions)}"
        assert isinstance(sample_quiz.questions[0], QuizQuestion), f"Expected QuizQuestion, got {type(sample_quiz.questions[0])}"
    
    def test_quiz_result_creation(self):
        """Testing Quiz Result Creation"""
        result = QuizResult(
            quiz_id="123e4567-e89b-12d3-a456-426614174000",
            user_name="John Doe",
            user_id="123e4567-e89b-12d3-a456-426614174001",
            score=85.0,
            total=100
        )
        assert result.quiz_id is not None, f"Expected non-None quiz_id, got {result.quiz_id}"
        assert result.user_id is not None, f"Expected non-None user_id, got {result.user_id}"
        assert result.score == 85.0, f"Expected 85.0, got {result.score}"
        assert result.total == 100, f"Expected 100, got {result.total}"
    def test_quiz_validation(self):
        """Testing Quiz model validation."""
        quiz = Quiz(title="Python Basics Quiz", questions=[])
        assert len(quiz.questions) == 0
        
        with pytest.raises(ValidationError):
            QuizResult(
                quiz_id="text",
                user_name="John Doe",
                user_id="text",
                score="eighty-five",  
                total="one hundred"  
            )       
class TestResponseModels:
    """Test ToolResponse, ErrorResponse, and SuccessResponse Models."""
    def test_response_models(self, sample_tool_response):
        """Testing ToolResponse models."""
        assert sample_tool_response.status == "success", f"Expected 'success', got {sample_tool_response.status}"
        assert sample_tool_response.data == {"key": "value"}, f"Expected {{'key': 'value'}}, got {sample_tool_response.data}"
        assert "success" in sample_tool_response.message, f"Expected 'success' in message, got {sample_tool_response.message}"
    
    def test_error_response_creation(self):
        """Testing ErrorResponse Creation."""
        error_response = ErrorResponse(
            status="error",
            error="File not found",
            details={"file": "test.txt"},
        )
        assert error_response.error == "File not found", f"Expected 'File not found', got {error_response.error}"
        assert error_response.details == {"file": "test.txt"}, f"Expected {{'file': 'test.txt'}}, got {error_response.details}"
        
    def test_success_response_creation(self):
        """Testing SuccessResponse Creation."""
        success_response = SuccessResponse(
            status="success",
            result={"id": "123", "name": "test"},
            message="Operation completed successfully"
        )
        assert success_response.status == "success", f"Expected 'success', got {success_response.status}"
        assert success_response.result == {"id": "123", "name": "test"}, f"Expected {{'id': '123', 'name': 'test'}}, got {success_response.result}"
        assert "successfully" in success_response.message, f"Expected 'successfully' in message, got {success_response.message}"
        
    def test_tool_response_serialization(self):
        """Testing ToolResponse serialization."""
        tool_response = ToolResponse(
            status="error", 
            data=None,
            message="An error occurred"
        )
        json_data = tool_response.model_dump()
        assert json_data["status"] == "error", f"Expected 'error', got {json_data['status']}"
        assert json_data["data"] is None
        assert json_data["message"] == "An error occurred", f"Expected 'An error occurred', got {json_data['message']}"
    
    def test_error_response_serialization(self):
        """Testing ErrorResponse serialization."""
        error_response = ErrorResponse(
            status="error",
            error="An unexpected error occurred",
            details={"code": 500}
        )
        json_data = error_response.model_dump()
        assert json_data["status"] == "error", f"Expected 'error', got {json_data['status']}"
        assert json_data["error"] == "An unexpected error occurred", f"Expected 'An unexpected error occurred', got {json_data['error']}"
        assert json_data["details"] == {"code": 500}, f"Expected {{'code': 500}}, got {json_data['details']}"
    
    def test_success_response_serialization(self):
        """Testing SuccessResponse serialization."""
        success_response = SuccessResponse(
            status="success",
            result={"data": "This is a successful response"},
            message="Operation completed successfully"
        )
        json_data = success_response.model_dump()
        assert json_data["status"] == "success", f"Expected 'success', got {json_data['status']}"
        assert json_data["result"] == {"data": "This is a successful response"}, f"Expected {{'data': 'This is a successful response'}}, got {json_data['result']}"
        assert json_data["message"] == "Operation completed successfully", f"Expected 'Operation completed successfully', got {json_data['message']}"
    
    def test_response_optional_fields(self):
        """Testing ToolResponse with optional fields."""
        minimal_response = ToolResponse(status="pending")
        assert minimal_response.data is None
        assert minimal_response.message is None
        
        minimal_error = ErrorResponse(status="error", error="An unexpected error occurred", details=None)
        assert minimal_error.details is None        
        
