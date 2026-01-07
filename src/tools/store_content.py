import os
from typing import Any, Dict, Literal
from src.services.content_manager import ContentManager, ContentStorageException

store_content_schema = {
    "type": "object",
    "properties": {
        "content_type": {
            "type": "string",
            "enum": ["url", "text"]
        },
        "source_url": {
            "type": "string"
        },
        "text": {
            "type": "string"
        },
        "custom_category": {
            "type": "string"
        },
        "custom_tags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["content_type"],
    "allOf": [
  {
    "if": { "properties": { "content_type": { "const": "url" } } },
    "then": { "required": ["source_url"] }
  },
  {
    "if": { "properties": { "content_type": { "enum": ["text", "code"] } } },
    "then": { "required": ["text"] }
  }
],
    "additionalProperties": False
}
def validate_with_schema(data: Dict, schema: Dict) -> None:
    from jsonschema import validate, ValidationError
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Input validation error: {e.message}")
def _mcp_text(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}    

def store_content(content_data: str, content_type: Literal["url", "text"], custom_category: str = None, custom_tags: list = None) ->Dict[str, Any]:
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
        validate_with_schema(content_data, store_content_schema)


        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        cm = ContentManager(openai_api_key=api_key)

        content_type = content_data.get("content_type")
        custom_category = content_data.get("custom_category")
        custom_tags = content_data.get("custom_tags", [])

        if content_type == "url":
            record = cm.store_content_from_url(
                url=content_data["source_url"],
                custom_category=custom_category,
                custom_tags=custom_tags
            )
        else:
            if content_type == "code" and "code" not in custom_tags:
                custom_tags.append("code")

            record = cm.store_content_from_text(
                text=content_data["text"],
                title=content_data.get("title"),
                custom_category=custom_category,
                custom_tags=custom_tags
            )
        results = (
            {"content_id": str(record.content_id),
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
    except Exception:
        return _mcp_text("Unexpected error while storing content.")
        
