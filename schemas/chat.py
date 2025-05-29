
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

class WeatherResponse(BaseModel):
    """Respond to the user with this"""

    STT: list[int] = Field(description="The number id of category")
    category: list[str] = Field(
        description="Name of category"
    )
    amount: list[int] = Field(description="The amount of the category")
    size: list[str] = Field(description="The size of the category")
    material: list[str] = Field(description="the material of the category")
    cost: list[int] = Field(description="The cost of category")


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        messages: List of messages in the conversation.
    """

    messages: str = Field(..., description="Response of Agent")
    data: WeatherResponse = Field(...,description="Data return by AI")


class Request(BaseModel):
    request:str


class StreamResponse(BaseModel):
    """Response model for streaming chat endpoint.

    Attributes:
        content: The content of the current chunk.
        done: Whether the stream is complete.
    """

    content: str = Field(default="", description="The content of the current chunk")
    done: bool = Field(default=False, description="Whether the stream is complete")

