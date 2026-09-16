from fastapi import APIRouter
from .auth import router as auth_router
from .documents import router as documents_router
from .sessions import router as sessions_router
from .interview import router as interview_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
api_router.include_router(interview_router, prefix="/interview", tags=["interview"])
