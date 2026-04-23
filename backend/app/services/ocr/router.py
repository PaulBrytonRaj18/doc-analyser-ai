"""
OCR Router - DocuLens AI v4.0
Routes OCR requests to appropriate engine based on content analysis
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Union

from app.core.config import settings
from app.services.ocr.preprocessor import ImagePreprocessor, PreprocessingResult
from app.services.ocr.tesseract_engine import TesseractEngine, TesseractResult
from app.services.ocr.easyocr_engine import EasyOCREngine, EasyOCRResult


@dataclass
class OCRResponse:
    full_text: str
    language_detected: str
    overall_confidence: float
    regions: List[dict] = field(default_factory=list)
    low_confidence_regions: List[int] = field(default_factory=list)
    preprocessing_applied: List[str] = field(default_factory=list)
    engine_used: str = "auto"


class OCRRouter:
    """Routes OCR between Tesseract (printed) and EasyOCR (handwriting)."""

    def __init__(self):
        self.engine = settings.ocr_engine
        self.preprocessor = ImagePreprocessor()
        self.tesseract = TesseractEngine()
        self.easyocr = EasyOCREngine()
        self.confidence_threshold = settings.ocr_confidence_threshold

    def scan(
        self,
        image: np.ndarray,
        language: Optional[str] = None,
        auto_preprocess: bool = True,
    ) -> OCRResponse:
        """
        Perform OCR with automatic engine selection.
        
        Strategy:
        1. If engine is "tesseract" - use Tesseract only
        2. If engine is "easyocr" - use EasyOCR only
        3. If engine is "auto":
           - First run Tesseract for printed text
           - If low confidence, use EasyOCR for handwriting
           - Combine results
        """
        # Preprocess if enabled
        preprocess_result: Optional[PreprocessingResult] = None
        if auto_preprocess and self.preprocessor.enabled:
            preprocess_result = self.preprocessor.enhance_for_ocr(image)
            image = preprocess_result.processed_image

        if self.engine == "tesseract":
            return self._scan_tesseract(image, language, preprocess_result)
        elif self.engine == "easyocr":
            return self._scan_easyocr(image, language, preprocess_result)
        else:
            return self._scan_auto(image, language, preprocess_result)

    def _scan_tesseract(
        self,
        image: np.ndarray,
        language: Optional[str],
        preprocess_result: Optional[PreprocessingResult],
    ) -> OCRResponse:
        """Scan using Tesseract only."""
        result = self.tesseract.recognize(image, language)

        return self._build_response(
            result.full_text,
            result.language_detected,
            result.overall_confidence,
            result.regions,
            result.low_confidence_regions,
            preprocess_result,
            result.engine_used,
        )

    def _scan_easyocr(
        self,
        image: np.ndarray,
        language: Optional[str],
        preprocess_result: Optional[PreprocessingResult],
    ) -> OCRResponse:
        """Scan using EasyOCR only."""
        result = self.easyocr.recognize(image, language)

        return self._build_response(
            result.full_text,
            result.language_detected,
            result.overall_confidence,
            result.regions,
            result.low_confidence_regions,
            preprocess_result,
            result.engine_used,
        )

    def _scan_auto(
        self,
        image: np.ndarray,
        language: Optional[str],
        preprocess_result: Optional[PreprocessingResult],
    ) -> OCRResponse:
        """Auto-select between Tesseract and EasyOCR."""
        # First try Tesseract
        tess_result = self.tesseract.recognize(image, language)
        
        if tess_result.overall_confidence >= 0.85:
            return self._build_response(
                tess_result.full_text,
                tess_result.language_detected,
                tess_result.overall_confidence,
                tess_result.regions,
                tess_result.low_confidence_regions,
                preprocess_result,
                tess_result.engine_used,
            )

        # Low confidence - try EasyOCR for handwriting
        easy_result = self.easyocr.recognize(image, language)

        if easy_result.overall_confidence > tess_result.overall_confidence:
            return self._build_response(
                easy_result.full_text,
                easy_result.language_detected,
                easy_result.overall_confidence,
                easy_result.regions,
                easy_result.low_confidence_regions,
                preprocess_result,
                easy_result.engine_used,
            )

        # Prefer Tesseract for printed text
        return self._build_response(
            tess_result.full_text,
            tess_result.language_detected,
            tess_result.overall_confidence,
            tess_result.regions,
            tess_result.low_confidence_regions,
            preprocess_result,
            tess_result.engine_used,
        )

    def _build_response(
        self,
        full_text: str,
        language: str,
        confidence: float,
        regions: List[Union[dict, object]],
        low_conf_regions: List[int],
        preprocess_result: Optional[PreprocessingResult],
        engine_used: str,
    ) -> OCRResponse:
        """Build standardized OCR response."""
        # Convert regions to dict format
        regions_list = []
        for r in regions:
            if hasattr(r, '__dict__'):
                regions_list.append({
                    "region_id": r.region_id,
                    "text": r.text,
                    "confidence": r.confidence,
                    "bounding_box": r.bounding_box if hasattr(r, 'bounding_box') else {},
                    "engine_used": engine_used,
                })
            elif isinstance(r, dict):
                regions_list.append(r)

        applied = preprocess_result.preprocessing_applied if preprocess_result else []

        return OCRResponse(
            full_text=full_text,
            language_detected=language,
            overall_confidence=confidence,
            regions=regions_list,
            low_confidence_regions=low_conf_regions,
            preprocessing_applied=applied,
            engine_used=engine_used,
        )

    def get_preview(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """Get preprocessing preview overlay."""
        return self.preprocessor.get_preview_overlay(
            image,
            self.preprocessor.enhance_for_ocr(image).processed_image,
        )


# Default instance
ocr_router = OCRRouter()