from pydantic import BaseModel, Field 
from typing import Any, Optional

class ToolResponse(BaseModel):
    """"Template for responses of the success or error of a tool."""
    status: str = Field(description="Status of the response such as 'success' or 'error')")
    data: Optional[Any] = None
    message: Optional[str] = None

class ErrorResponse(ToolResponse):
    """Response structure for errors."""
    error: str = Field(description="Error message")
    details: Optional[Any] = None

class SuccessResponse(ToolResponse):
    """Response structure for successful operations."""
    result: Optional[Any] = Field(description="The result of the successes")
    message: Optional[str]