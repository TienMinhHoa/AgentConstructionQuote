
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from typing import Optional

class WeatherResponse(BaseModel):
    """Respond to the user with this"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    amount: list[int] = Field(description="The amount of the category")
    size: list[str] = Field(description="The size of the category")
    unit: list [str] = Field(description="The unit to measure size")
    material: list[str] = Field(description="the material of the category")
    cost: list[int] = Field(description="The cost of category")
    location: list[str] = Field(description="The location of that category belongs to")


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        messages: List of messages in the conversation.
    """

    messages: str = Field(..., description="Response of Agent")
    data: Optional[WeatherResponse] = None


class Request(BaseModel):
    request:str
    special_request: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    session_id: str


class StreamResponse(BaseModel):
    """Response model for streaming chat endpoint.

    Attributes:
        content: The content of the current chunk.
        done: Whether the stream is complete.
    """

    content: str = Field(default="", description="The content of the current chunk")
    done: bool = Field(default=False, description="Whether the stream is complete")

