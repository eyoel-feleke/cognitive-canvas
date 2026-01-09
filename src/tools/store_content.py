import os
from typing import Any, Dict, Literal, List
from src.services.content_manager import ContentManager, ContentStorageException
from dataclasses import dataclass

@dataclass
class ContentData:
    title: str
    text: str
    content_type: Literal["url", "text", "code"]
    source_url: str = None
    custom_category: str = None
    custom_tags: list = None

def validate_with_schema(data: Dict, schema: Dict) -> None:
    from jsonschema import validate, ValidationError
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Input validation error: {e.message}")
def _mcp_text(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}    

def store_content(content_data: ContentData) ->Dict[str, Any]:
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
    # MCP tool: store content
    try:


        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        cm = ContentManager(openai_api_key=api_key)

        content_type = content_data.content_type
        custom_category = content_data.custom_category
        custom_tags = content_data.custom_tags or []

        stored_records = []
        if  "url" in content_type:
            record = cm.store_content_from_url(
                url=content_data.source_url,
                custom_category=custom_category,
                custom_tags=custom_tags
            )
            stored_records.append(record)
        
        if "text" in content_type or "code" in content_type:
            if "code" in content_type and "code" not in custom_tags:
                custom_tags.append("code")

            record = cm.store_content_from_text(
                text=content_data.text,
                title=content_data.title,
                custom_category=custom_category,
                custom_tags=custom_tags
            )
            stored_records.append(record)

        results = (
            {"content_ids": stored_records,
             "title": record.title,
             "summary": record.summary,
             "category": record.category,
             "tags": record.tags}
        )
        return _mcp_text(results)
    
    except ValueError as e:
        return _mcp_text(f"{str(e)}")
    except ContentStorageException as e:
        return _mcp_text(f"Content storage failed: {str(e)}")
    except Exception as e:
        return _mcp_text(f"Unexpected error while storing content: {str(e)}")
        



if __name__ == "__main__":
    # Example usage
    content_data = {
      "content_data": "http://example.com/ml-basics",
      "content_type": "url",
      "custom_category": "Machine Learning",
      "custom_tags": [
        "machine-learning",
        "ai",
        "python"
      ]
    }
    result = store_content(content_data, content_data["content_type"], content_data.get("custom_category"), content_data.get("custom_tags"))
    print(result)