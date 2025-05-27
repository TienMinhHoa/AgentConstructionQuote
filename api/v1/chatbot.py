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
    Request,
    WeatherResponse
)

router = APIRouter()
agent = RootGraph()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_request: Request,
):
    try:

        result = await agent.chat(
            user_request.request
        )
        if "final_response" in result.keys():
            response = result["final_response"].dict()
            print(response)
        else:
            response = {
                "STT":[],
                "category":[],
                "cost":[]
            }

        return ChatResponse(messages=result["messages"][-1].content, data = WeatherResponse(**response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


