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