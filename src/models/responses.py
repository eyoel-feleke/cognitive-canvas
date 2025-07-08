from pydantic import BaseModel
from typing import Any, Optional

class ToolResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Any] = None

class SuccessResponse(BaseModel):
    result: Any
    message: Optional[str] = None
