"""
API v1 Router - Unified API routing.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import documents, rag, analysis, analyze, ocr, compare, batch, webhooks, upload

api_router = APIRouter(prefix="/v1")

api_router.include_router(documents.router)
api_router.include_router(rag.router)
api_router.include_router(analysis.router)
api_router.include_router(analyze.router)
api_router.include_router(ocr.router)
api_router.include_router(compare.router)
api_router.include_router(batch.router)
api_router.include_router(webhooks.router)
api_router.include_router(upload.router)
