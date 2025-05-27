
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        messages: List of messages in the conversation.
    """

    messages: str = Field(..., description="Response of Agent")


class Request(BaseModel):
    request:str


