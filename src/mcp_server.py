from src.tools import store_content, generate_quiz, query_content
from src.tools.store_content import ContentData
from src.tools.query_content import QueryContentRequest
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
        
    
    def store_content_tool(self, content_data: ContentData):
        """Stores and categorizes content data.
        Args:
            content_data (Dict): The content data to be stored.
            content_type (Literal["url", "text"]): Type of content ("url", "text").
                - source_url (str, optional): URL of the content if content_type is "url".
                - text (str, optional): Text content if content_type is "text".
            custom_category (str, optional): Custom category for the content.
            custom_tags (List[str], optional): Custom tags for the content.
        Returns:
            Dict[str, Any]: Result of the storage operation.
            - content_id (str): The unique identifier of the stored content.
            - title (str): The title of the stored content.
            - summary (str): A brief summary of the stored content.
            - category (str): The category assigned to the content.
            - tags (List[str]): The tags associated with the content.
        Raises:
            ValueError: If input validation fails.
            ContentStorageException: If content storage fails.
        """
        try:
            return store_content(content_data)
        except Exception as e:
            return f"Error storing content: {(e)}"

    def query_content_tool(self, query_request: QueryContentRequest):
        """ Query stored content using date ranges or categories.
        Args:
            query_text : The query parameters for content search.
            start_date (str, optional): Start date for date range query in ISO format (YYYY-MM-DDTHH:MM:SS).
            end_date (str, optional): End date for date range query in ISO format (YYYY-MM-DDTHH:MM:SS).
            category (str, optional): Category for category-based query.
            k (int, optional): Number of top results to return. Defaults to 5.
        Returns:
            Dict[str, Any]: The query results from the vector database. 
            - results (List[Dict]): List of content records matching the query.
        Raises:
            ValueError: If input validation fails.
            VectorDatabaseError: If the query operation fails.
        """
        try:
            return query_content(query_request)
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