from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4

class QuizQuestion(BaseModel):
    """The structure for what the quiz question will look like."""
    number: int = Field(default=1)
    topic: str = Field(description="The topic where the question is based on")
    question: str
    explanation: str
    choice: List[str] = Field(description="List of possible choices for the question")

class Quiz(BaseModel):
    """Complete Quiz structure"""
    title: str = Field(description="Title of the article it is based on")
    quiz_id: UUID = Field(default_factory=uuid4, frozen=True)
    questions: List[QuizQuestion] = Field(default_factory=list)

class QuizResult(BaseModel):
    """A way to record the results taken by the user."""
    quiz_id: UUID = Field(default_factory=uuid4, frozen=True)
    user_name: str
    user_id: UUID = Field(default_factory=uuid4, frozen=True)
    score: float
    total: int

# Example of proper model usage and serialization
if __name__ == "__main__":
    # Create a quiz question
    question = QuizQuestion(
        number=1,
        tag="Python",
        question="What is the output of print(2 ** 3)?",
        explanation="2 raised to the power of 3 equals 8.",
        choice=["6", "7", "8", "9"]
    )
    
    # Create a quiz with the question
    quiz = Quiz(
        title="Python Basics Quiz",
        questions=[question]
    )
    
    # Create a quiz result
    result = QuizResult(
        user_name="John Doe",
        score=85.0,
        total=100
    )
    
    # Test serialization
    question_json = question.model_dump_json()
    quiz_json = quiz.model_dump_json()
    result_json = result.model_dump_json()
    
    # Test deserialization
    QuizQuestion.model_validate_json(question_json)
    Quiz.model_validate_json(quiz_json)
    QuizResult.model_validate_json(result_json)

