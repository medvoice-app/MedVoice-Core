from fastapi import APIRouter

from .endpoints.post import llm, rag_system
from .endpoints.get import minio_storage
from .endpoints import nurse, process_audio

api_router = APIRouter()

api_router.include_router(llm.router, prefix="/test/llm", tags=["test-llm"])
api_router.include_router(minio_storage.router, tags=["minio-storage"])
api_router.include_router(nurse.router, prefix="/nurses", tags=["nurses"])
api_router.include_router(process_audio.router, tags=["audio-processing"])
api_router.include_router(rag_system.router, tags=["rag-system"])
