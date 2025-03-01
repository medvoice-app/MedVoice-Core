from fastapi import APIRouter

from .endpoints.post import llm, rag_system
from .endpoints.get import gcloud_storage
from .endpoints import audio_processing, nurse

api_router = APIRouter()

api_router.include_router(llm.router, prefix="/test/llm", tags=["test-llm"])
api_router.include_router(gcloud_storage.router, tags=["gcloud-storage"])
api_router.include_router(nurse.router, prefix="/nurses", tags=["nurses"])
api_router.include_router(audio_processing.router, tags=["audio-processing"])
api_router.include_router(rag_system.router, tags=["rag-system"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for container orchestration and monitoring.
    """
    return {"status": "healthy", "message": "API is operational"}