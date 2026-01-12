from datetime import datetime
from typing import Dict, Any
from src.services.vector_database import VectorDatabase, VectorDatabaseError
from dataclasses import dataclass
@dataclass
class QueryContentRequest:
    query_text: str
    start_date: str = None
    end_date: str = None
    category: str = None
    k: int = 5

def query_content(request: QueryContentRequest) -> Dict[str, Any]:
    """ Query stored content using date ranges or categories.
    Args:
        query_text : The query parameters for content search.
        start_date (str, optional): Start date for date range query in ISO format (YYYY-MM-DDThh-mm-ss).
        end_date (str, optional): End date for date range query in ISO format (YYYY-MM-DDThh-mm-ss).
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
        
        vd = VectorDatabase()

        k = request.k
        if request.start_date and request.end_date:
            start_date = datetime.fromisoformat(request.start_date)
            end_date = datetime.fromisoformat(request.end_date)
            results = vd.query_by_date_range(
                start_date=start_date,
                end_date=end_date,
                k=k
            )
        elif request.category:
            results = vd.get_by_category(
                category=request.category,
                limit=k
            )
        else:
            raise ValueError("Either date_range or category must be provided for querying content.")
        return {"results": results}
    except Exception as e:
        raise VectorDatabaseError(f"Failed to query content: {str(e)}")
