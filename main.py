"""This file contains the main application entry point."""

from datetime import datetime
from typing import (
    Any,
    Dict,
)

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.v1.api import api_router


# Load environment variables
load_dotenv()

app = FastAPI(host="0.0.0.0",
              port=8000,)


origins = [
    "*",  # IP của máy frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # hoặc ["*"] để cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root(request: Request):
    """Root endpoint returning basic API information."""
    return {
        "swagger_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:

    # Check database connectivity
    response = {
        "timestamp": datetime.now().isoformat(),
    }

    # If DB is unhealthy, set the appropriate status code
    status_code = status.HTTP_200_OK

    return JSONResponse(content=response, status_code=status_code)


def main():
    port = 8000
    uvicorn.run(
            "main:app", 
            host="0.0.0.0",
            port=port,
            reload=True,
        )
