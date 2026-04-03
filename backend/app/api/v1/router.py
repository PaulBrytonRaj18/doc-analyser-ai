"""
API v1 Router - Unified API routing.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import documents, rag, analysis

api_router = APIRouter(prefix="/v1")

api_router.include_router(documents.router)
api_router.include_router(rag.router)
api_router.include_router(analysis.router)
