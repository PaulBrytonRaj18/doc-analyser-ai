"""
Tesseract OCR Engine - DocuLens AI v4.0
Wrapper for Tesseract OCR with confidence scoring
"""

import pytesseract
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from app.core.config import settings


@dataclass
class OCRRegion:
    region_id: int
    text: str
    confidence: float
    bounding_box: Dict[str, int]
    words: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TesseractResult:
    full_text: str
    language_detected: str
    overall_confidence: float
    regions: List[OCRRegion] = field(default_factory=list)
    low_confidence_regions: List[int] = field(default_factory=list)
    engine_used: str = "tesseract"


class TesseractEngine:
    """Tesseract OCR engine wrapper for printed text."""

    def __init__(self):
        self.lang = settings.ocr_default_language
        self.confidence_threshold = settings.ocr_confidence_threshold
        self._setup_tesseract()

    def _setup_tesseract(self):
        """Configure Tesseract executable path if needed."""
        tesseract_cmd = settings.tesseract_cmd if hasattr(settings, 'tesseract_cmd') else None
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def recognize(
        self,
        image: Any,
        language: Optional[str] = None,
    ) -> TesseractResult:
        """
        Perform OCR on image using Tesseract.
        
        Args:
            image: NumPy array (OpenCV image) or path to image file
            language: Language code (e.g., 'eng', 'tam', 'hin')
        """
        lang = language or self.lang

        try:
            # Get detailed OCR data with bounding boxes
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                output_type=pytesseract.Output.DICT,
                config='--psm 6 --oem 3',
            )

            # Extract text and regions
            regions = []
            full_text_parts = []
            confidences = []
            low_conf_ids = []

            n_boxes = len(data['text'])
            current_region = []
            region_id = 0

            for i in range(n_boxes):
                text = data['text'][i].strip()
                if not text:
                    continue

                conf = int(data['conf'][i])
                confidences.append(conf)

                # Create bounding box
                bbox = {
                    "x": data['left'][i],
                    "y": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i],
                }

                word_info = {
                    "text": text,
                    "confidence": conf / 100.0,
                    "bounding_box": bbox,
                }

                # Group words into regions (lines)
                if data['block_num'][i] != (data['block_num'][i-1] if i > 0 else -1):
                    if current_region:
                        region_text = " ".join([w["text"] for w in current_region])
                        region_conf = sum(w["confidence"] for w in current_region) / len(current_region)
                        
                        regions.append(OCRRegion(
                            region_id=region_id,
                            text=region_text,
                            confidence=region_conf,
                            bounding_box=bbox,
                            words=current_region,
                        ))
                        
                        if region_conf < self.confidence_threshold:
                            low_conf_ids.append(region_id)
                        
                        full_text_parts.append(region_text)
                        region_id += 1
                    
                    current_region = [word_info]
                else:
                    current_region.append(word_info)

            # Add last region
            if current_region:
                region_text = " ".join([w["text"] for w in current_region])
                region_conf = sum(w["confidence"] for w in current_region) / len(current_region)
                
                regions.append(OCRRegion(
                    region_id=region_id,
                    text=region_text,
                    confidence=region_conf,
                    bounding_box=bbox,
                    words=current_region,
                ))
                
                if region_conf < self.confidence_threshold:
                    low_conf_ids.append(region_id)
                
                full_text_parts.append(region_text)

            full_text = "\n".join(full_text_parts)
            overall_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            # Detect language
            detected_lang = self._detect_language(image, lang)

            return TesseractResult(
                full_text=full_text,
                language_detected=detected_lang,
                overall_confidence=overall_conf,
                regions=regions,
                low_confidence_regions=low_conf_ids,
            )

        except Exception as e:
            return TesseractResult(
                full_text="",
                language_detected=lang,
                overall_confidence=0.0,
                regions=[],
                low_confidence_regions=[],
            )

    def _detect_language(
        self,
        image: Any,
        default_lang: str,
    ) -> str:
        """Detect language in image."""
        try:
            # Use Tesseract's language detection
            langs = pytesseract.get_languages(config='')
            
            # For now, return default
            return default_lang

        except Exception:
            return default_lang

    def get_available_languages(self) -> List[str]:
        """Get list of available Tesseract languages."""
        try:
            return pytesseract.get_languages(config='')
        except Exception:
            return [self.lang]


# Default instance
tesseract_engine = TesseractEngine()