from typing import Dict
from src.services.vector_database import VectorDatabase, VectorDatabaseError

def query_content(query_text: Dict) -> Dict[str, Any]:
    """ Query stored content using date ranges or categories.
    Args:
        query_text (Dict): The query parameters for content search.
         - date_range (Dict, optional): Date range for filtering content.
             - start_date (str): Start date in ISO format (YYYY-MM-DD).
             - end_date (str): End date in ISO format (YYYY-MM-DD).
         - category (str, optional): Category to filter content.
         - k (int, optional): Number of top similar results to return. Defaults to 5.
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

        start_date = query_text.get("date_range", {}).get("start_date")
        end_date = query_text.get("date_range", {}).get("end_date")
        category = query_text.get("category")
        k = query_text.get("k", 5)

        if start_date and end_date:
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
