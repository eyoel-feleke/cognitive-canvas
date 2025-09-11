from unittest.mock import patch
from src.services.quiz_service import QuizService
from src.models.quiz import Quiz, QuizQuestion, QuizResult
import pytest

def test_generate_quiz_success():
    service = QuizService(api_key="test-api-key")
    
    # Mock multiple choice quiz
    mock_mcq_quiz = Quiz(
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

    # Mock true/false quiz
    mock_tf_quiz = Quiz(
        type="true_false",
        title="Test Quiz",
        quiz_id="123e4567-e89b-12d3-a456-426614174000",
        questions=[
            QuizQuestion(
                number=1,
                topic="Test Topic",
                question="The sky is blue.",
                explanation="The sky appears blue due to the scattering of sunlight.",
                choice=["True", "False"]
            ),
            QuizQuestion(
                number=2,
                topic="Test Topic",
                question="The Earth is flat.",
                explanation="The Earth is spherical in shape.",
                choice=["True", "False"]
            )
        ]
    )

    # Mock fill in the blank quiz
    mock_fib_quiz = Quiz(
        type="fill_in_the_blank",
        title="Test Quiz",
        quiz_id="123e4567-e89b-12d3-a456-426614174000",
        questions=[
            QuizQuestion(
                number=1,
                topic="Test Topic",
                question="The largest planet in our solar system is _____.",
                explanation="The largest planet in our solar system is Jupiter.",
                choice=["Jupiter", "Saturn", "Earth", "Mars"]
            ),
            QuizQuestion(
                number=2,
                topic="Test Topic",
                question="The process by which plants make their food is called _____.",
                explanation="The process by which plants make their food is called photosynthesis.",
                choice=["Photosynthesis", "Respiration", "Transpiration", "Germination"]
            )
        ]
    )

    # Test multiple choice quiz generation
    with patch.object(service.client.chat.completions, 'create', return_value=mock_mcq_quiz):
        quiz1 = service.generate_mcq_quiz(
            content_summaries=["This is a test summary."],
            category="General Knowledge",
            num_questions=2,
            difficulty="easy"
        )
    assert isinstance(quiz1, Quiz), "Returned object is not of type Quiz"
    assert len(quiz1.questions) == 2, "Number of questions does not match"
    assert quiz1.title == "Test Quiz", "Quiz title does not match"
    assert quiz1.type == "multiple_choice", "Quiz type should be multiple_choice"
    
    # Test true/false quiz generation
    with patch.object(service.client.chat.completions, 'create', return_value=mock_tf_quiz):
        quiz2 = service.generate_true_false_quiz(
            content_summaries=["This is a test summary."],
            category="General Knowledge",
            num_questions=2,
            difficulty="easy"
        )
    assert isinstance(quiz2, Quiz), "Returned object is not of type Quiz"
    assert len(quiz2.questions) == 2, "Number of questions does not match"
    assert quiz2.title == "Test Quiz", "Quiz title does not match"
    assert quiz2.type == "true_false", "Quiz type should be true_false"
    
    # Test fill in the blank quiz generation
    with patch.object(service.client.chat.completions, 'create', return_value=mock_fib_quiz):
        quiz3 = service.generate_fill_in_blank_quiz(
            content_summaries=["This is a test summary."],
            category="General Knowledge",
            num_questions=2,
            difficulty="easy"
        )
    assert isinstance(quiz3, Quiz), "Returned object is not of type Quiz"
    assert len(quiz3.questions) == 2, "Number of questions does not match"
    assert quiz3.title == "Test Quiz", "Quiz title does not match"
    assert quiz3.type == "fill_in_the_blank", "Quiz type should be fill_in_the_blank"