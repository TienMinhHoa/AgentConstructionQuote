"""Chatbot API endpoints for handling chat interactions.

This module provides endpoints for chat interactions, including regular chat,
streaming chat, message history management, and chat history clearing.
"""

import json
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import StreamingResponse
from core.graph import RootGraph
from schemas.chat import (
    ChatResponse,
    Request
)

router = APIRouter()
agent = RootGraph()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
):
    try:

       
        result = await agent.chat(
            request.request
        )

        return ChatResponse(messages=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


