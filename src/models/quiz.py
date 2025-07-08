from pydantic import BaseModel
from typing import List

class QuizQuestion(BaseModel):
    question: str
    explanation: str

class Quiz(BaseModel):
    title: str
    questions: List[QuizQuestion]

class QuizResult(BaseModel):
    quiz_id: str
    user_id: str
    score: int
    total: int
