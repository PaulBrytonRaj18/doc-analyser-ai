"""
Image Processing Service with OCR support.
"""

import io
from typing import Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import for optional dependencies
_tesseract = None
_easyocr = None
_pil = None


def _get_pil():
    global _pil
    if _pil is None:
        try:
            from PIL import Image

            _pil = Image
        except ImportError:
            logger.warning("Pillow not installed. Image processing disabled.")
            _pil = False
    return _pil


def _check_tesseract():
    global _tesseract
    if _tesseract is None:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            _tesseract = True
        except Exception:
            _tesseract = False
    return _tesseract


def _check_easyocr():
    global _easyocr
    if _easyocr is None:
        try:
            import easyocr

            _easyocr = True
        except Exception:
            _easyocr = False
    return _easyocr


class ImageProcessor:
    """Extract text from images using OCR."""

    def extract_text(self, file_bytes: bytes) -> Tuple[str, dict]:
        """Extract text from image using OCR."""
        metadata = {"num_pages": 1, "file_type": "image"}

        Image = _get_pil()
        if not Image:
            return "Image processing not available. Please install Pillow.", metadata

        try:
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size
            metadata["image_dimensions"] = f"{width}x{height}"

            text = ""

            if _check_tesseract():
                text = self._extract_tesseract(image)
            elif _check_easyocr():
                text = self._extract_easyocr(file_bytes)
            else:
                logger.warning("No OCR library available, using PIL text extraction")
                text = self._extract_pil_text(image)

            if not text.strip():
                logger.warning("OCR returned empty text")
                text = "Image content detected but no text could be extracted. OCR library may not be installed."

            metadata["ocr_confidence"] = "medium"

        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            text = f"Image file processed. Text extraction not available: {str(e)}"

        return text, metadata

    def _extract_pil_text(self, image) -> str:
        """Fallback: Try to extract any embedded text from image metadata."""
        if hasattr(image, "text"):
            return image.text.get("Title", "") or image.text.get("Description", "")
        return ""

    def _extract_tesseract(self, image) -> str:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract

            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    def _extract_easyocr(self, file_bytes: bytes) -> str:
        """Extract text using EasyOCR."""
        try:
            import easyocr

            reader = easyocr.Reader(["en"], gpu=False)
            results = reader.readfile(file_bytes)
            text_parts = [result[1] for result in results]
            return " ".join(text_parts)
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return ""


image_processor = ImageProcessor()
