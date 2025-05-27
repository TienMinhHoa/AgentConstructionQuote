from fastapi import APIRouter

from api.v1.chatbot import router as chatbot_router

api_router = APIRouter()

api_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status information.
    """
    return {"status": "healthy", "version": "1.0.0"}
