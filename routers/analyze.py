"""
Document analysis router.
Endpoints: POST /api/v1/analyze, POST /api/v1/analyze/batch
"""

import time
import asyncio
import json
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, Response

from models.schemas import AnalysisResponse, SummaryResult, EntitySet, SentimentResult
from services.pdf_extractor import extract_text_from_pdf
from services.docx_extractor import extract_text_from_docx
from services.image_extractor import extract_text_from_image
from services.ai_analyzer import analyze_with_ai
from utils.file_handler import detect_file_type, validate_file, count_words
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyse a document",
    description="Upload a PDF, DOCX, or image file. Returns AI-generated classification, summary, entities, and sentiment.",
)
async def analyze_document(
    file: UploadFile = File(..., description="PDF, DOCX, or image file to analyse"),
):
    start_time = time.perf_counter()
    filename = file.filename or "unknown"
    processing_steps = ["uploaded"]
    logger.info(f"📄 Received file: {filename} ({file.content_type})")

    # Read file bytes
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Validate
    is_valid, error_msg = validate_file(file_bytes, filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Detect file type
    file_type, mime_type = detect_file_type(file_bytes, filename)
    logger.info(f"Detected type: {file_type} ({mime_type})")

    # Extract text
    try:
        extracted_text = await asyncio.get_event_loop().run_in_executor(
            None, _extract_text, file_type, file_bytes
        )
        if file_type == "image":
            processing_steps.append("ocr_complete")
        processing_steps.append("text_extracted")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Text extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the document. For images, ensure text is clear and visible.",
        )

    word_count = count_words(extracted_text)
    logger.info(f"Extracted {word_count} words from {filename}")

    # AI Analysis
    try:
        ai_result = await asyncio.get_event_loop().run_in_executor(
            None, analyze_with_ai, extracted_text
        )
        processing_steps.append("analysis_complete")
    except Exception as e:
        logger.error(f"AI analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(f"✅ Completed in {elapsed_ms}ms — {filename}")

    # Build response
    summary_data = ai_result.get("summary", {})
    entities = ai_result.get("entities", {})
    sentiment_data = ai_result.get("sentiment", {})

    return AnalysisResponse(
        status="success",
        filename=filename,
        file_type=file_type,
        word_count=word_count,
        document_type=ai_result.get("document_type", "Other"),
        summary=SummaryResult(
            bullets=summary_data.get("bullets", []),
            tldr=summary_data.get("tldr", ""),
        ),
        entities=EntitySet(
            people=entities.get("people", []),
            organizations=entities.get("organizations", []),
            dates=entities.get("dates", []),
            amounts=entities.get("amounts", []),
        ),
        sentiment=SentimentResult(
            label=sentiment_data.get("label", "neutral"),
            confidence=sentiment_data.get("confidence", 50),
            reason=sentiment_data.get("reason", ""),
        ),
        processing_steps=processing_steps,
        processing_time_ms=elapsed_ms,
    )


@router.post(
    "/analyze/batch",
    summary="Analyse multiple documents",
    description="Upload multiple files for batch analysis.",
)
async def analyze_batch(
    files: List[UploadFile] = File(..., description="Multiple PDF, DOCX, or image files"),
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch.")

    results = []
    errors = []

    for file in files:
        try:
            result = await analyze_document(file)
            results.append(result.model_dump())
        except HTTPException as e:
            errors.append({"filename": file.filename, "error": e.detail})
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    return {"results": results, "errors": errors, "total": len(files)}


@router.post("/export/json", summary="Export analysis result as JSON file")
async def export_json(
    file: UploadFile = File(..., description="File to analyse and export"),
):
    result = await analyze_document(file)
    json_bytes = json.dumps(result.model_dump(), indent=2).encode("utf-8")
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{result.filename}_analysis.json"'},
    )


@router.post("/export/summary", summary="Export analysis result as markdown summary")
async def export_summary(
    file: UploadFile = File(..., description="File to analyse and export as summary"),
):
    result = await analyze_document(file)
    r = result.model_dump()

    md_lines = [
        f"# Document Analysis: {r['filename']}",
        "",
        f"**Document Type:** {r['document_type']}",
        f"**File Type:** {r['file_type'].upper()} · **Words:** {r['word_count']:,}",
        f"**Processing Time:** {r['processing_time_ms']:.0f}ms",
        "",
        "## Summary",
        "",
        f"**TL;DR:** {r['summary']['tldr']}",
        "",
    ]
    for bullet in r["summary"]["bullets"]:
        md_lines.append(f"- {bullet}")

    md_lines += [
        "",
        "## Sentiment",
        "",
        f"**{r['sentiment']['label'].capitalize()}** (confidence: {r['sentiment']['confidence']}%)",
        f"_{r['sentiment']['reason']}_",
        "",
        "## Entities",
        "",
    ]
    for key, label in [("people", "People"), ("organizations", "Organizations"), ("dates", "Dates"), ("amounts", "Amounts")]:
        items = r["entities"].get(key, [])
        if items:
            md_lines.append(f"**{label}:** {', '.join(items)}")

    md_content = "\n".join(md_lines)
    return Response(
        content=md_content.encode("utf-8"),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{result.filename}_summary.md"'},
    )


def _extract_text(file_type: str, file_bytes: bytes) -> str:
    """Sync wrapper for text extraction (runs in executor)."""
    if file_type == "pdf":
        text, _ = extract_text_from_pdf(file_bytes)
        return text
    elif file_type == "docx":
        text, _ = extract_text_from_docx(file_bytes)
        return text
    elif file_type == "image":
        text, engine = extract_text_from_image(file_bytes)
        logger.info(f"OCR engine used: {engine}")
        return text
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
