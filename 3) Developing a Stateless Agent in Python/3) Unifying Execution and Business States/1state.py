from typing import List, Any, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    # TODO: Add id field as a required string
    id: str
    
    # TODO: Add steps field as an integer with default value 0
    steps: int = 0
    
    # TODO: Add status field as a string with default value "running"
    status: str = "running"
    
    # TODO: Add context field as List[Any] using Field(default_factory=list)
    context: List[Any] = Field(default_factory=list)
    
    # TODO: Add pending_tool_calls field as List[Any] using Field(default_factory=list)
    pending_tool_calls: List[Any] = Field(default_factory=list)
    
    # TODO: Add error field as Optional[str] with default None
    error: Optional[str] = None
    
    # TODO: Add final_answer field as Optional[str] with default None
    final_answer: Optional[str] = None