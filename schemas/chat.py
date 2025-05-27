
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


