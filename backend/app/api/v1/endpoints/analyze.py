"""
Document Analyzer API Endpoint.
Main entry point for document analysis (PDF, DOCX, Images).
"""

import time
import hashlib
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import JSONResponse

from app.models.schemas import (
    DocumentAnalysisResponse,
    EntityExtraction,
    AnalysisMetadata,
    DocumentAnalyzeRequest,
)
from app.services.processing import file_processor, ai_processing_service
from app.services.processing.text_preprocessing import text_preprocessor
from app.services.document.document_service import document_service
from app.services.vector.vector_store import vector_store_service
from app.services.embedding.embedding_service import embedding_service
from app.core.config import settings
from app.core.security import verify_api_key
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze", tags=["Document Analyzer"])


@router.post(
    "", response_model=DocumentAnalysisResponse, dependencies=[Depends(verify_api_key)]
)
async def analyze_document(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, or Image)"),
    query: Optional[str] = Form(None, description="Optional query for RAG retrieval"),
):
    """
    Analyze a document file and extract:
    - Summary
    - Named Entities (persons, organizations, dates, locations, monetary values)
    - Sentiment (positive/negative/neutral)
    """
    start_time = time.time()

    try:
        file_bytes = await file.read()

        file_processor.validate_file(file_bytes, file.content_type)

        extracted_text, processing_metadata = file_processor.process_file(
            file_bytes=file_bytes,
            content_type=file.content_type,
            filename=file.filename,
        )

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file",
            )

        cleaned_text = text_preprocessor.clean_text(extracted_text)

        ai_results = ai_processing_service.analyze_document(cleaned_text)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        processing_time_str = (
            f"{processing_time_ms / 1000:.2f}s"
            if processing_time_ms > 1000
            else f"{processing_time_ms}ms"
        )

        document_id = hashlib.md5(file_bytes[:1000]).hexdigest()[:12]

        num_pages = processing_metadata.get("num_pages", 1)
        if isinstance(num_pages, str):
            num_pages = num_pages
        else:
            num_pages = str(num_pages) if num_pages else "1"

        response_data = {
            "document_id": document_id,
            "summary": ai_results["summary"],
            "entities": EntityExtraction(
                persons=ai_results["entities"].get("persons", []),
                organizations=ai_results["entities"].get("organizations", []),
                dates=ai_results["entities"].get("dates", []),
                locations=ai_results["entities"].get("locations", []),
                monetary_values=ai_results["entities"].get("monetary_values", []),
            ),
            "sentiment": ai_results["sentiment"],
            "metadata": AnalysisMetadata(
                file_type=processing_metadata.get("file_type", "unknown"),
                processing_time=processing_time_str,
                num_pages=num_pages,
            ),
        }

        logger.info(f"Document analyzed successfully: {file.filename}")

        return DocumentAnalysisResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post(
    "/text",
    response_model=DocumentAnalysisResponse,
    dependencies=[Depends(verify_api_key)],
)
async def analyze_text(
    text: str = Form(..., description="Text content to analyze"),
):
    """
    Analyze raw text content directly.
    """
    start_time = time.time()

    try:
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text provided",
            )

        cleaned_text = text_preprocessor.clean_text(text)

        ai_results = ai_processing_service.analyze_document(cleaned_text)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        processing_time_str = (
            f"{processing_time_ms / 1000:.2f}s"
            if processing_time_ms > 1000
            else f"{processing_time_ms}ms"
        )

        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]

        return DocumentAnalysisResponse(
            document_id=text_hash,
            summary=ai_results["summary"],
            entities=EntityExtraction(
                persons=ai_results["entities"].get("persons", []),
                organizations=ai_results["entities"].get("organizations", []),
                dates=ai_results["entities"].get("dates", []),
                locations=ai_results["entities"].get("locations", []),
                monetary_values=ai_results["entities"].get("monetary_values", []),
            ),
            sentiment=ai_results["sentiment"],
            metadata=AnalysisMetadata(
                file_type="text/plain",
                processing_time=processing_time_str,
                num_pages="1",
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )
