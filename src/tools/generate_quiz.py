import mcp
import src.services.quiz_service as QuizService
from src.models.quiz import Quiz
from typing import List, Literal



@mcp.tool()
def generate_quiz(quiz_type:Literal["multiple choice", "fill in the blank", "true or false"], content_summaries: List[str],
                      category: str, num_questions: int = 5,
                      difficulty: str = "mixed") -> Quiz:
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
    allowed_types = ["multiple_choice", "true_false", "short_answer"]
    allowed_difficulties = ["easy", "medium", "hard", "mixed"]
    # Input validation
    if not quiz_type_lower or not quiz_type_lower in allowed_types:
        raise ValueError("Type must be one of the following strings: multiple choice, fill in the blank, true or false.")
    if not category or isinstance(category, str) == False:
        raise ValueError("Category must be a non-empty string.")
    if not isinstance(num_questions, int) or num_questions <= 0:
        raise ValueError("Number of questions must be a positive integer.")
    if difficulty not in allowed_difficulties:
        raise ValueError("Difficulty must be one of: easy, medium, hard, mixed.")
    # Generate the quiz based on the specified type
    try:
            if quiz_type_lower == "multiple_choice":
                quiz = QuizService().generate_multiple_choice_quiz(
                    content_summaries=[f"Category: {category}"],
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            elif quiz_type_lower == "true_false":
                quiz = QuizService().generate_true_false_quiz(
                    content_summaries=[f"Category: {category}"],
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            elif quiz_type_lower == "short_answer":
                quiz = QuizService().generate_short_answer_quiz(
                    content_summaries=[f"Category: {category}"],
                    category=category,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
            else:
                return "Unsupported quiz type."
    except Exception as e:
        return RuntimeError(f"Quiz generation failed: {e}")
    except ValueError as e:
        return ValueError(f"Invalid input: {e}") 
    
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
