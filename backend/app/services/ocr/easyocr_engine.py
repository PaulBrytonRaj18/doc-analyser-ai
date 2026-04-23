"""
EasyOCR Engine - DocuLens AI v4.0
Wrapper for EasyOCR with handwriting support
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from app.core.config import settings


@dataclass
class EasyOCRRegion:
    region_id: int
    text: str
    confidence: float
    bounding_box: List[List[int]]
    words: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EasyOCRResult:
    full_text: str
    language_detected: str
    overall_confidence: float
    regions: List[EasyOCRRegion] = field(default_factory=list)
    low_confidence_regions: List[int] = field(default_factory=list)
    engine_used: str = "easyocr_handwriting"


class EasyOCREngine:
    """EasyOCR engine wrapper for handwritten and degraded text."""

    def __init__(self):
        self.lang = [settings.ocr_default_language]
        self.confidence_threshold = settings.ocr_confidence_threshold
        self.reader = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy load EasyOCR model."""
        if self._model_loaded:
            return

        try:
            import easyocr
            self.reader = easyocr.Reader(
                self.lang,
                gpu=False,
                verbose=False,
            )
            self._model_loaded = True
        except Exception:
            self._model_loaded = False

    def recognize(
        self,
        image: np.ndarray,
        language: Optional[str] = None,
    ) -> EasyOCRResult:
        """
        Perform OCR on image using EasyOCR.
        
        Args:
            image: NumPy array (OpenCV image)
            language: Language code
        """
        self._load_model()

        if self.reader is None:
            return EasyOCRResult(
                full_text="",
                language_detected=language or self.lang[0],
                overall_confidence=0.0,
                regions=[],
                low_confidence_regions=[],
            )

        try:
            # Run EasyOCR
            results = self.reader.readtext(
                image,
                batch_size=8,
                workers=0,
            )

            regions = []
            full_text_parts = []
            confidences = []
            low_conf_ids = []
            region_id = 0

            for idx, (bbox, text, conf) in enumerate(results):
                confidences.append(conf)
                
                region = EasyOCRRegion(
                    region_id=region_id,
                    text=text,
                    confidence=conf,
                    bounding_box=bbox,
                    words=[{
                        "text": text,
                        "confidence": conf,
                        "bounding_box": bbox,
                    }],
                )
                regions.append(region)
                
                full_text_parts.append(text)
                
                if conf < self.confidence_threshold:
                    low_conf_ids.append(region_id)
                
                region_id += 1

            full_text = " ".join(full_text_parts)
            overall_conf = sum(confidences) / len(confidences) if confidences else 0.0

            return EasyOCRResult(
                full_text=full_text,
                language_detected=language or self.lang[0],
                overall_confidence=overall_conf,
                regions=regions,
                low_confidence_regions=low_conf_ids,
            )

        except Exception as e:
            return EasyOCRResult(
                full_text="",
                language_detected=language or self.lang[0],
                overall_confidence=0.0,
                regions=[],
                low_confidence_regions=[],
            )

    def is_available(self) -> bool:
        """Check if EasyOCR is available."""
        self._load_model()
        return self._model_loaded

    def get_available_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ["en", "ta", "hi", "zh", "ja", "ko", "fr", "de", "es", "it", "pt", "ru"]


# Default instance
easyocr_engine = EasyOCREngine()