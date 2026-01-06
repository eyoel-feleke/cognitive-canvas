from typing import Any, Dict
from src.services.content_manager import ContentManager

def store_content(content_data: Dict, Any) ->Dict[str, Any]:
    """Stores and categorizes content data.
    Args:
        content_data (Dict): The content data to be stored.
    Returns:
        Dict[str, Any]: Result of the storage operation.
    """
    # MCP tool: store content
    try:
        # validate input
        input_type = content_data.get("content_type", "").lower()

        cm = ContentManager()
        result = None

        if input_type == "url":
            if not content_data.get("source_url"):
                raise ValueError("source_url is required for content_type 'url'.")
        if input_type == "text":
            if not content_data.get("text"):
                raise ValueError("text is required for content_type 'text'.")
        if input_type == "url":
            url = content_data.get("source_url")
            custom_category = content_data.get("custom_category")
            custom_tags = content_data.get("custom_tags", [])
            try:
                record = cm.store_url_content(
                    url=url, 
                    custom_category=custom_category, 
                    custom_tags=custom_tags)
            except Exception as e:
                raise ValueError(f"Failed to store URL content: {str(e)}")
            result = {
                "title": record.title,
                "content_id": str(record.content_id),
                "summary": record.summary,
                "category": record.category,
                "tags": record.tags,
                "content_type": record.content_type,
                "source_url": record.source_url,
                "metadata": {
                    "author": record.metadata.author,
                    "date_published": record.metadata.date_published.isoformat(),
                    "abstract": record.metadata.abstract,
                    "keywords": record.metadata.keywords,
                    "citation": record.metadata.citation
                }
            }
        elif input_type == "text":
            text = content_data.get("text")
            custom_category = content_data.get("custom_category")
            custom_tags = content_data.get("custom_tags", [])
            try:
                record = cm.store_text_content(
                    text=text, 
                    custom_category=custom_category, 
                    custom_tags=custom_tags)
            except Exception as e:
                raise ValueError(f"Failed to store text content: {str(e)}")
            result = {
                "title": record.title,
                "content_id": str(record.content_id),
                "summary": record.summary,
                "category": record.category,
                "tags": record.tags,
                "content_type": record.content_type,
                "source_url": record.source_url,
                "metadata": {
                    "author": record.metadata.author,
                    "date_published": record.metadata.date_published.isoformat(),
                    "abstract": record.metadata.abstract,
                    "keywords": record.metadata.keywords,
                    "citation": record.metadata.citation
                }
            }
        else:
            raise ValueError("Unsupported content_type. Supported types are 'url' and 'text'.")
        return result
    except Exception as e:
        raise ValueError(f"Error storing content: {str(e)}")
    except ValueError as ve:
        raise f'"Input validation error: {str(ve)}"'
        
