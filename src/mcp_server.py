from src.tools import store_content, generate_quiz, query_content
from mcp.server.fastmcp import FastMCP
from typing import List, Literal
import logging

log = logging.getLogger(__name__)
class MCPServer:
    
    def __init__(self, name="cognitive-canvas"):
        self.mcp = FastMCP(name)
        self._setup_tools()

    def _setup_tools(self):
        self.mcp.tool()(self.store_content_tool)
        self.mcp.tool()(self.query_content_tool)
        self.mcp.tool()(self.generate_quiz_tool)
        
    
    def store_content_tool(self):
        try:
            return store_content()
        except Exception as e:
            return f"Error storing content: {(e)}"

    def query_content_tool(self): 
        try:
            return query_content()
        except Exception as e:
            return f"Error querying content: {(e)}"

    def generate_quiz_tool(self, quiz_type: Literal["multiple_choice", "fill_in_the_blank", "true_or_false"], 
                          content_summaries: List[str], category: str, 
                          num_questions: int = 5, difficulty: Literal["easy", "medium", "hard", "mixed"] = "mixed"): 
        """Generate a quiz based on content summaries.
        
        Args:
            quiz_type: Type of quiz to generate (multiple choice, fill in the blank, or true or false)
            content_summaries: List of content summaries to base the quiz on
            category: The category of the quiz
            num_questions: Number of questions in the quiz (default: 5)
            difficulty: Difficulty level of the quiz (default: mixed)
        """
        try:
            log.info(f"Generating quiz of type: {quiz_type}, category: {category}, num_questions: {num_questions}, difficulty: {difficulty}")
            return generate_quiz(quiz_type, content_summaries, category, num_questions, difficulty)
        except Exception as e:
            return f"Error generating quiz: {(e)}"
    
    def run_mcp_server(self):
        self.mcp.run()