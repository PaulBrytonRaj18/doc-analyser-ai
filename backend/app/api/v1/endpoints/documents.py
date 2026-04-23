"""
Document Management API Endpoints.
"""

import json
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from app.models.schemas import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentBatchRequest,
    DocumentBatchResponse,
    DocumentDeleteResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
)
from app.services.document.document_service import document_service
from app.services.llm.llm_service import llm_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(request: DocumentIngestRequest):
    """Ingest a document for RAG processing."""
    try:
        result = document_service.process_document(
            text=request.text,
            filename=request.filename,
            file_type=request.file_type,
            file_size=len(request.text),
            document_type=request.document_type,
            summary=request.summary,
            tags=request.tags,
            metadata=request.metadata,
            chunking_strategy=request.chunking_strategy,
        )

        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error)

        return DocumentIngestResponse(
            status="success",
            document_id=result.document_id,
            filename=result.metadata.filename,
            file_type=result.metadata.file_type,
            total_chunks=result.chunks_created,
            processing_time_ms=result.processing_time_ms,
            metadata=result.metadata.to_dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/file", response_model=DocumentIngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None),
    chunking_strategy: str = Query("recursive"),
):
    """Upload and ingest a file."""
    try:
        contents = await file.read()
        text = contents.decode("utf-8", errors="ignore")

        if not text.strip():
            raise HTTPException(
                status_code=400, detail="File contains no extractable text"
            )

        result = document_service.process_document(
            text=text,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            file_size=len(contents),
            document_type=document_type,
            chunking_strategy=chunking_strategy,
        )

        if result.status == "failed":
            raise HTTPException(status_code=500, detail=result.error)

        return DocumentIngestResponse(
            status="success",
            document_id=result.document_id,
            filename=result.metadata.filename,
            file_type=result.metadata.file_type,
            total_chunks=result.chunks_created,
            processing_time_ms=result.processing_time_ms,
            metadata=result.metadata.to_dict(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch", response_model=DocumentBatchResponse)
async def ingest_batch(request: DocumentBatchRequest):
    """Batch ingest multiple documents."""
    results = []
    successful = 0
    failed = 0

    for doc in request.documents:
        result = document_service.process_document(
            text=doc.text,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=len(doc.text),
            document_type=doc.document_type,
            summary=doc.summary,
            tags=doc.tags,
            metadata=doc.metadata,
            chunking_strategy=request.chunking_strategy,
        )

        results.append(
            {
                "document_id": result.document_id,
                "filename": result.metadata.filename,
                "status": result.status,
                "chunks_created": result.chunks_created,
                "error": result.error,
            }
        )

        if result.status == "success":
            successful += 1
        else:
            failed += 1

    return DocumentBatchResponse(
        total=len(results), successful=successful, failed=failed, results=results
    )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """Delete a document and its chunks."""
    try:
        success = document_service.delete_document(document_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document")

        return DocumentDeleteResponse(
            status="success",
            document_id=document_id,
            message="Document deleted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze document content with AI."""
    try:
        system_prompt = """You are an expert document analyzer. Analyze the document and provide:
1. A brief summary (2-3 sentences)
2. Key points (3-5 bullet points)
3. Document type classification
4. Named entities (people, organizations, dates, amounts)
5. Sentiment (positive, negative, neutral) with confidence 0-100

Respond in JSON format."""

        prompt = f"Analyze this document:\n\n{request.text[:15000]}"

        response = await llm_service.generate(
            prompt=prompt, system_instruction=system_prompt, max_tokens=1500
        )

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            analysis = {
                "summary": response.content[:500],
                "key_points": [],
                "document_type": "Unknown",
                "entities": {},
                "sentiment": "neutral",
            }

        return DocumentAnalysisResponse(
            status="success",
            document_id=request.document_id or "unknown",
            summary=analysis.get("summary", ""),
            key_points=analysis.get("key_points", []),
            document_type=analysis.get("document_type", "Unknown"),
            entities=analysis.get("entities", {}),
            sentiment=analysis.get("sentiment", {"label": "neutral", "confidence": 50}),
            word_count=len(request.text.split()),
        )

    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
