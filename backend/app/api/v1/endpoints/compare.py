"""
Analysis Endpoints - DocuLens AI v4.0
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Form, HTTPException

from app.models.schemas import (
    CompareResponse,
    RedactRequest,
    RedactResponse,
)


router = APIRouter(tags=["Analysis"])


@router.get("/analyze/{document_id}")
async def get_analysis(document_id: str):
    """Get cached auto-analysis for a document."""
    from app.services.document.document_service import document_service
    
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "analysis": doc.get("analysis", {}),
    }


@router.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    """Analyze raw text without file upload."""
    from app.services.analysis.auto_analysis import auto_analysis_service
    
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    result = auto_analysis_service.analyze(document_id, text)
    
    return {
        "document_id": document_id,
        "classification": result.classification,
        "summary": result.summary,
        "entities": result.entities,
        "sentiment": result.sentiment,
        "key_insights": result.key_insights,
        "processing_time_ms": result.processing_time_ms,
    }


@router.post("/compare")
async def compare_documents(
    document_id_a: str = Form(...),
    document_id_b: str = Form(...),
    focus: Optional[str] = Form(None),
) -> CompareResponse:
    """Compare two documents semantically."""
    from app.services.document.comparator import document_comparator
    from app.services.document.document_service import document_service
    
    doc1 = document_service.get_document(document_id_a)
    doc2 = document_service.get_document(document_id_b)
    
    if not doc1 or not doc2:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text1 = doc1.get("content_text", "")
    text2 = doc2.get("content_text", "")
    
    result = document_comparator.compare(text1, text2, doc1, doc2, focus)
    
    return CompareResponse(
        document1=result.document1,
        document2=result.document2,
        overall_similarity=result.overall_similarity,
        content_overlap=result.overall_similarity,
        semantic_similarity=result.overall_similarity,
        similar_sections=result.similar_sections,
        key_differences=result.key_differences,
        processing_time_ms=result.processing_time_ms,
    )


@router.post("/redact")
async def redact_document(request: RedactRequest) -> RedactResponse:
    """Redact PII from a document."""
    from app.services.document.redactor import redactor_service
    from app.services.document.document_service import document_service
    
    doc = document_service.get_document(request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text = doc.get("content_text", "")
    result = redactor_service.redact(text, request.pii_types, request.replacement)
    
    return RedactResponse(
        document_id=request.document_id,
        status="success",
        redacted_text=result.redacted_text,
        redactions_applied=result.redactions_applied,
        processing_time_ms=0,
    )