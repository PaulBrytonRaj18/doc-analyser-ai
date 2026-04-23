"""OCR Services - DocuLens AI v4.0"""

from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.tesseract_engine import TesseractEngine
from app.services.ocr.easyocr_engine import EasyOCREngine
from app.services.ocr.router import OCRRouter
from app.services.ocr.confidence import ConfidenceScorer
from app.services.ocr.language import LanguageDetector

__all__ = [
    "ImagePreprocessor",
    "TesseractEngine",
    "EasyOCREngine",
    "OCRRouter",
    "ConfidenceScorer",
    "LanguageDetector",
]