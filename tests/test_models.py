from datetime import datetime
from src.models.content import ContentMetadata, ContentRecord
from src.models.quiz import Quiz, QuizQuestion, QuizResult
from src.models.responses import ErrorResponse, SuccessResponse, ToolResponse


def test_content_metadata():
    """Test the ContentMetadata model."""
    metadata = ContentMetadata(
        title="Sample Metadata",
        author="Author Name",
        abstract="This is a synopsis of the sample metadata.",
        keywords=["keyword1", "keyword2"],
        date_published=datetime.now()
    )

    metadata_json = metadata.model_dump_json()
    ContentMetadata.model_validate_json(metadata_json)  # just runs
    assert True
def test_content_record():
    """Test the ContentRecord model."""
    metadata = ContentMetadata(
        title="Sample Metadata",
        author="Author Name",
        abstract="This is a synopsis of the sample metadata.",
        keywords=["keyword1", "keyword2"],
        date_published=datetime.now()
    )

    content_record = ContentRecord(
        original_content="This is a sample content.",
        content_type="text",
        title="Sample Content",
        summary="This is a summary of the sample content.",
        category="General",
        tags=["sample", "content"],
        embedding=[0.1, 0.2, 0.3],
        timestamp=datetime.now(),
        metadata=metadata
    )

    content_json = content_record.model_dump_json()
    ContentRecord.model_validate_json(content_json)  
    assert True 

def test_quiz_models():
    """Test the Quiz, QuizQuestion, and QuizResult models."""
    question = QuizQuestion(
        number=1,
        topic="Python",
        question="What is the output of print(2 ** 3)?",
        explanation="2 raised to the power of 3 equals 8.",
        choice=["6", "7", "8", "9"]
    )
    
    quiz = Quiz(
        title="Python Basics Quiz",
        questions=[question]
    )
    
    result = QuizResult(
        user_name="John Doe",
        score=85.0,
        total=100
    )
    
    question_json = question.model_dump_json()
    quiz_json = quiz.model_dump_json()
    result_json = result.model_dump_json()
    
    QuizQuestion.model_validate_json(question_json)
    Quiz.model_validate_json(quiz_json)
    QuizResult.model_validate_json(result_json)
    
    assert True
def test_response_models():
    """Test ToolResponse, ErrorResponse, and SuccessResponse models."""
    # Create instances
    tool_response = ToolResponse(
        status="pending",
        data={"step": 1},
        message="Processing request"
    )
    
    error_response = ErrorResponse(
        status="error",
        error="File not found",
        details={"file": "test.txt"},
        message="Unable to process request"
    )
    
    success_response = SuccessResponse(
        status="success",
        result={"id": "123", "name": "test"},
        message="Operation completed successfully"
    )
    
    tool_json = tool_response.model_dump_json()
    error_json = error_response.model_dump_json()
    success_json = success_response.model_dump_json()
    
    ToolResponse.model_validate_json(tool_json)
    ErrorResponse.model_validate_json(error_json)
    SuccessResponse.model_validate_json(success_json)
    
    assert True


if __name__ == "__main__":
    test_content_metadata()
    test_content_record()
    test_response_models()
    test_quiz_models()
    print("All tests passed")
