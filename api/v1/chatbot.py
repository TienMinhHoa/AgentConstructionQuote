"""Chatbot API endpoints for handling chat interactions.

This module provides endpoints for chat interactions, including regular chat,
streaming chat, message history management, and chat history clearing.
"""

from prometheus_client import Counter, Histogram, Gauge
llm_stream_duration_seconds = Histogram(
    "llm_stream_duration_seconds",
    "Time spent processing LLM stream inference",
    ["model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

import json
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from fastapi.responses import StreamingResponse
from core.graph import RootGraph
from schemas.chat import (
    ChatResponse,
    Request,
    WeatherResponse,
    StreamResponse
)

router = APIRouter()
agent = RootGraph()


@router.post("/chat", response_model=ChatResponse,status_code=status.HTTP_200_OK)
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


@router.post("/stream_chat",status_code=status.HTTP_200_OK)
async def stream_chat(
    user_request: Request
):
    try:
        async def event_generator():
            try:
                full_response = ""
                with llm_stream_duration_seconds.labels(model="gemini-flash-2.5").time():
                    async for chunk in agent.stream_chat(
                        user_request.request
                    ):
                        full_response += chunk
                        response = StreamResponse(content=chunk, done=False)
                        yield f"data: {json.dumps(response.model_dump())}\n\n"
                    
                    final_response = StreamResponse(content="", done=True)
                    yield f"data: {json.dumps(final_response.model_dump())}\n\n"
            except Exception as e:
                error_response = StreamResponse(content=str(e), done=True)
                yield f"data: {json.dumps(error_response.model_dump())}\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



