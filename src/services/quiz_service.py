from openai import OpenAI
import instructor
from typing import List
import os

from src.models.quiz import Quiz, QuizQuestion, QuizResult

api_key = os.getenv("OPENAI_API_KEY")

class QuizService:
    def __init__(self, api_key: str):
        self.client = instructor.from_openai(OpenAI(api_key=api_key))
    
    def generate_mcq_quiz(self, content_summaries: List[str], 
                    category: str, num_questions: int = 5, difficulty: str = "mixed") -> Quiz:
        """Generate multiple choice quiz from content summaries"""
        if not content_summaries or all(s.strip() == "" for s in content_summaries):
            raise ValueError("Content summaries cannot be blank.")
        if num_questions <= 0:
            raise ValueError("Number of questions must be greater than zero.")
        if difficulty not in ["easy", "medium", "hard", "mixed"]:
            raise ValueError("difficulty must be: easy, medium, hard, or mixed.")
        
        combined_content = "\n\n".join(content_summaries)
        
        prompt = f"""
        Create a {num_questions}-question multiple choice quiz based on the following content from the {category} category.
        
        Content:
        {combined_content}
        
        Requirements:
        - Each question should have 4 options
        - Include explanations for correct answers
        - Mix of difficulty levels : {difficulty}
        - Focus on key concepts and facts
        """
        
        try:    
            quiz = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_model=Quiz
            )
            
            # Validate quiz questions
            for q in quiz.questions:
                if len(q.choice) != 4:
                    raise ValueError(f"Question '{q.number}' should have 4 choices.")
                if not q.explanation.strip():
                    raise ValueError(f"Explanation is missing for question {q.number}.")
            
            return quiz
        except Exception as e:
            raise RuntimeError(f"Failed to generate quiz: {e}")

    def generate_fill_in_blank_quiz(self, content_summaries: List[str], 
                                    category: str, num_questions: int = 5, difficulty: str = "mixed") -> Quiz:
        """Generate fill-in-the-blank quiz from content summaries"""
        if not content_summaries or all(s.strip() == "" for s in content_summaries):
            raise ValueError("Content summaries cannot be blank.")
        if num_questions <= 0:
            raise ValueError("Number of questions must be greater than zero.")
        if difficulty not in ["easy", "medium", "hard", "mixed"]:
            raise ValueError("difficulty must be: easy, medium, hard, or mixed.")
        
        combined_content = "\n\n".join(content_summaries)
        
        prompt = f"""
        Create a {num_questions}-question fill-in-the-blank quiz based on the following content from the {category} category.
        
        Content:
        {combined_content}
        
        Requirements:
        - Each question should have a fill-in-the-blank format
        - Include explanations for correct answers
        - Mix of difficulty levels : {difficulty}
        - Focus on key concepts and facts
        """
        
        try:    
            quiz = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_model=Quiz
            )
            
            # Validate quiz questions
            for q in quiz.questions:
                if len(q.choice) < 2:
                    raise ValueError(f"Question '{q.number}' should have at least 2 choices.")
                if not q.explanation.strip():
                    raise ValueError(f"Explanation is missing for question {q.number}.")
            
            return quiz
        except Exception as e:
            raise RuntimeError(f"Failed to generate quiz: {e}")

    def generate_true_false_quiz(self, content_summaries: List[str],
                                    category: str, num_questions: int = 5, difficulty: str = "mixed") -> Quiz:
        """Generate true/false quiz from content summaries"""
        if not content_summaries or all(s.strip() == "" for s in content_summaries):
            raise ValueError("Content summaries cannot be blank.")
        if num_questions <= 0:
            raise ValueError("Number of questions must be greater than zero.")
        if difficulty not in ["easy", "medium", "hard", "mixed"]:
            raise ValueError("difficulty must be: easy, medium, hard, or mixed.")
        
        combined_content = "\n\n".join(content_summaries)
        
        prompt = f"""
        Create a {num_questions}-question true/false quiz based on the following content from the {category} category.
        
        Content:
        {combined_content}
        
        Requirements:
        - Each question should have a true/false format
        - Include explanations for correct answers
        - Mix of difficulty levels : {difficulty}
        - Focus on key concepts and facts
        """
        
        try:    
            quiz = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_model=Quiz
            )
            
            # Validate quiz questions
            for q in quiz.questions:
                if len(q.choice) != 2:
                    raise ValueError(f"Question '{q.number}' should have exactly 2 choices (True/False).")
                if not q.explanation.strip():
                    raise ValueError(f"Explanation is missing for question {q.number}.")
            
            return quiz
        except Exception as e:
            raise RuntimeError(f"Failed to generate quiz: {e}")