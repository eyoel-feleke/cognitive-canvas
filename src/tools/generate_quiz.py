from mcp.server.fastmcp import FastMCP
from src.services.quiz_service import QuizService
from src.models.quiz import Quiz
from typing import List, Literal
import os


def generate_quiz(quiz_type:Literal["multiple_choice", "fill_in_the_blank", "true_or_false"], content_summaries: List[str],
                      category: str, num_questions: int = 5,
                      difficulty: Literal["easy", "medium", "hard", "mixed"] = "mixed") -> Quiz:
    """Generates a quiz based on content summaries.
    Args:
        quiz_type (Literal["multiple choice", "fill in the blank", "true or false"]): Type of quiz to generate.
        content_summaries (List[str]): List of content summaries to base the quiz on.
        category (str): The category of the quiz.
        num_questions (int, optional): Number of questions in the quiz. Defaults to 5.
        difficulty (str, optional): Difficulty level of the quiz. Defaults to "mixed".
    Returns:
        Quiz: Generated quiz object based on the type of quiz requested.
    """
    # Normalize quiz type input
    quiz_type_lower = quiz_type.lower().strip() if isinstance(quiz_type, str) else ""
    allowed_types = ["multiple_choice", "true_false", "fill_in_the_blank"]
    allowed_difficulties = ["easy", "medium", "hard", "mixed"]
    # Input validation
    if not quiz_type_lower or quiz_type_lower not in allowed_types:
        raise ValueError("Type must be one of the following strings: multiple choice, fill in the blank, true or false.")
    if not category or isinstance(category, str) == False:
        raise ValueError("Category must be a non-empty string.")
    if not isinstance(num_questions, int) or num_questions <= 0:
        raise ValueError("Number of questions must be a positive integer.")
    if difficulty not in allowed_difficulties:
        raise ValueError("Difficulty must be one of: easy, medium, hard, mixed.")
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    
    # Initialize quiz service
    quiz_service = QuizService(api_key=api_key)
    
    # Generate the quiz based on the specified type
    try:
            if quiz_type_lower == "multiple_choice":
                quiz = quiz_service.generate_mcq_quiz(
                    content_summaries=content_summaries,
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            elif quiz_type_lower == "true_false":
                quiz = quiz_service.generate_true_false_quiz(
                    content_summaries=content_summaries,
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            elif quiz_type_lower == "fill_in_the_blank":
                quiz = quiz_service.generate_fill_in_blank_quiz(
                    content_summaries=content_summaries,
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            else:
                raise ValueError(f"Unsupported quiz type: {quiz_type_lower}")
    except Exception as e:
        raise RuntimeError(f"Quiz generation failed: {e}") 
    
    # Outoutput the generated quiz
    output = [
        f"Generated {quiz_type_lower} quiz with {len(quiz.questions)} questions in the category '{category}' with difficulty '{difficulty}'.",
    ]
    for i , question in enumerate(quiz.questions, start=1):
        output.append(f"Q{i}: {question.question}")
        if question.choice:
            for idx, choice in enumerate(question.choice, start=1):
                output.append(f"   {idx}. {choice}")
        output.append(f"   Explanation: {question.explanation}")
    return quiz


## Example usage
if __name__ == "__main__":
    sample_quiz = generate_quiz(
        quiz_type="multiple choice",
        content_summaries=["Python is a high-level, interpreted programming language known for its readability and versatility."],
        category="Programming",
        num_questions=3,
        difficulty="easy"
    )
    print(sample_quiz)
