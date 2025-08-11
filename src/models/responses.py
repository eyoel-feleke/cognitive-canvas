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

# Example of proper model usage and serialization
if __name__ == "__main__":
    # Test basic ToolResponse
    tool_response = ToolResponse(
        status="pending",
        data={"step": 1},
        message="Processing request"
    )
    
    # Test ErrorResponse
    error_response = ErrorResponse(
        status="error",
        error="File not found",
        details={"file": "test.txt"},
        message="Unable to process request"
    )
    
    # Test SuccessResponse
    success_response = SuccessResponse(
        status="success",
        result={"id": "123", "name": "test"},
        message="Operation completed successfully"
    )
    
    # Test serialization
    tool_json = tool_response.model_dump_json()
    error_json = error_response.model_dump_json()
    success_json = success_response.model_dump_json()
    
    # Test deserialization
    ToolResponse.model_validate_json(tool_json)
    ErrorResponse.model_validate_json(error_json)
    SuccessResponse.model_validate_json(success_json)
    
    print("All serialization tests passed!")
