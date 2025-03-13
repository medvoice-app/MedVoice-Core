from fastapi import APIRouter

from .endpoints import nurse

api_router = APIRouter()

# Include the nurse router with the appropriate prefix
api_router.include_router(nurse.router, prefix="/nurses", tags=["nurses"])
