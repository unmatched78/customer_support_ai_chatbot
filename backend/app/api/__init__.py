from fastapi import APIRouter
from .endpoints import chat_router, admin_router
from .endpoints.organizations import router as organizations_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])

__all__ = ["api_router"]