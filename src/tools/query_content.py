from datetime import datetime
from typing import Dict, Any
from src.services.vector_database import VectorDatabase, VectorDatabaseError

def query_content(query_text: str, start_date: str = None, end_date: str = None, category: str = None, k: int = 5) -> Dict[str, Any]:
    """ Query stored content using date ranges or categories.
    Args:
        query_text : The query parameters for content search.
        start_date (str, optional): Start date for date range query in ISO format (YYYY-MM-DD).
        end_date (str, optional): End date for date range query in ISO format (YYYY-MM-DD).
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
        # Validate input
        if not isinstance(query_text, dict):
            raise ValueError("Query text must be a dictionary.")
        vd = VectorDatabase()

        k = query_text.get("k", 5)
        if start_date and end_date:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            results = vd.query_by_date_range(
                start_date=start_date,
                end_date=end_date,
                k=k
            )
        elif category:
            results = vd.get_by_category(
                category=category,
                limit=k
            )
        else:
            raise ValueError("Either date_range or category must be provided for querying content.")
        # fromat mcp results for 
        return {"results": results}
    except Exception as e:
        raise VectorDatabaseError(f"Failed to query content: {str(e)}")
