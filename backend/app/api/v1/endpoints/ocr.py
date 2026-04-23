"""
OCR Endpoints - DocuLens AI v4.0
"""

import io
import time
import uuid
from typing import Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from PIL import Image

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.schemas import (
    OCRScanRequest,
    OCRScanResponse,
    OCRLanguagesResponse,
    OCRPreviewResponse,
)


router = APIRouter(prefix="/ocr", tags=["OCR"])

MAX_FILE_SIZE = settings.max_file_size_bytes


def read_image_from_file(file: UploadFile) -> np.ndarray:
    """Convert uploaded file to OpenCV image."""
    contents = file.file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    image = Image.open(io.BytesIO(contents))
    
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    return np.array(image)


@router.post("/scan", response_model=OCRScanResponse)
async def ocr_scan(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    auto_preprocess: bool = Form(True),
) -> OCRScanResponse:
    """
    Perform OCR on an image file.
    
    - **file**: Image file (PNG, JPG, etc.)
    - **language**: Language code (default: eng)
    - **auto_preprocess**: Enable preprocessing pipeline
    """
    start_time = time.time()
    
    try:
        image = read_image_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    from app.services.ocr import ocr_router
    
    result = ocr_router.scan(
        image=image,
        language=language,
        auto_preprocess=auto_preprocess,
    )
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    return OCRScanResponse(
        document_id=document_id,
        ocr_result={
            "full_text": result.full_text,
            "language_detected": result.language_detected,
            "overall_confidence": result.overall_confidence,
            "regions": result.regions,
            "low_confidence_regions": result.low_confidence_regions,
            "preprocessing_applied": result.preprocessing_applied,
        },
        processing_time_ms=processing_time_ms,
    )


@router.post("/scan/preview")
async def ocr_scan_preview(
    file: UploadFile = File(...),
) -> OCRPreviewResponse:
    """
    Get preprocessing preview with OCR overlay.
    
    Useful for debugging OCR issues.
    """
    try:
        image = read_image_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    from app.services.ocr import ocr_router
    
    preview_image = ocr_router.get_preview(image)
    
    # Get Tesseract result on original
    tesseract_result = ocr_router.tesseract.recognize(image, None)
    
    return OCRPreviewResponse(
        original_size=list(image.shape),
        processed_size=list(preview_image.shape),
        ocr_overlay=tesseract_result.full_text if tesseract_result else "",
    )


@router.post("/languages")
async def ocr_detect_languages(
    file: UploadFile = File(...),
) -> OCRLanguagesResponse:
    """
    Detect language in an image.
    """
    try:
        image = read_image_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    from app.services.ocr.language import language_detector
    
    # Get text first
    from app.services.ocr import ocr_router
    result = ocr_router.scan(image, auto_preprocess=False)
    
    if result.full_text:
        lang_detected = language_detector.detect_from_text(result.full_text)
    else:
        from app.services.ocr.language import DetectedLanguage
        lang_detected = [DetectedLanguage("en", 0.5)]
    
    languages = [
        {"language": l.language, "confidence": l.confidence}
        for l in lang_detected
    ]
    
    return OCRLanguagesResponse(languages=languages)