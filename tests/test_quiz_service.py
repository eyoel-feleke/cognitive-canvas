from unittest.mock import patch
from src.services.quiz_service import QuizService
from src.models.quiz import Quiz, QuizQuestion, QuizResult
import pytest

def test_generate_quiz_success():
    service = QuizService(api_key="test-api-key")
    
    mock_quiz = Quiz(
        type="multiple_choice",
        title="Test Quiz", 
        quiz_id="123e4567-e89b-12d3-a456-426614174000",
        questions=[
            QuizQuestion(
                number=1,
                topic="Test Topic",
                question="What is 2 + 2?",
                explanation="2 + 2 equals 4.",
                choice=["3", "4", "5", "6"]
            ),
            QuizQuestion(
                number=2,
                topic="Test Topic",
                question="What is the capital of France?",
                explanation="The capital of France is Paris.",
                choice=["Berlin", "Madrid", "Paris", "Rome"]
            )
        ]
    )
    with patch.object(service.client.chat.completions, 'create', return_value=mock_quiz) as mock_create:
        quiz = service.generate_quiz(
            content_summaries=["This is a test summary."],
            category="General Knowledge",
            num_questions=2,
            difficulty="easy"
        )
        
    assert isinstance(quiz, Quiz), "Returned object is not of type Quiz"
    assert len(quiz.questions) == 2, "Number of questions does not match"
    assert quiz.title == "Test Quiz", "Quiz title does not match"