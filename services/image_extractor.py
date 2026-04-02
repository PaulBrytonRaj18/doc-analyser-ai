"""
Image text extraction via OCR.
Primary: pytesseract (Tesseract)
Fallback: easyocr
"""

import io
from typing import Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_image(file_bytes: bytes) -> Tuple[str, str]:
    """
    Extract text from image bytes using OCR.
    Returns (extracted_text, ocr_engine_used)
    """
    # Pre-process image for better OCR
    processed_bytes = _preprocess_image(file_bytes)

    # Try tesseract first
    try:
        text, engine = _tesseract_ocr(processed_bytes)
        if text.strip():
            logger.info(f"Tesseract OCR: {len(text)} chars extracted")
            return text, engine
    except Exception as e:
        logger.warning(f"Tesseract failed: {e}, trying EasyOCR")

    # Fallback: EasyOCR
    try:
        text, engine = _easyocr_extract(file_bytes)
        if text.strip():
            logger.info(f"EasyOCR: {len(text)} chars extracted")
            return text, engine
    except Exception as e:
        logger.warning(f"EasyOCR failed: {e}")

    # Last fallback: return empty with note
    logger.error("All OCR engines failed")
    raise ValueError("OCR extraction failed: no text could be detected in the image")


def _preprocess_image(file_bytes: bytes) -> bytes:
    """Enhance image for better OCR accuracy"""
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        import io as _io

        img = Image.open(_io.BytesIO(file_bytes))

        # Convert to RGB if needed
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Scale up small images
        width, height = img.size
        if width < 1000 or height < 1000:
            scale = max(1000 / width, 1000 / height, 1.5)
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        # Convert to grayscale for OCR
        img = img.convert("L")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # Save processed image
        output = _io.BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}, using original")
        return file_bytes


def _tesseract_ocr(image_bytes: bytes) -> Tuple[str, str]:
    """Extract text using pytesseract"""
    import pytesseract
    from PIL import Image
    import io as _io

    img = Image.open(_io.BytesIO(image_bytes))

    # Use multiple page segmentation modes for best results
    configs = [
        "--oem 3 --psm 6",   # Assume a uniform block of text
        "--oem 3 --psm 3",   # Fully automatic page segmentation
        "--oem 3 --psm 4",   # Assume a single column of text
    ]

    best_text = ""
    for config in configs:
        try:
            text = pytesseract.image_to_string(img, config=config, lang="eng")
            if len(text.strip()) > len(best_text.strip()):
                best_text = text
        except Exception:
            continue

    return best_text.strip(), "tesseract"


def _easyocr_extract(image_bytes: bytes) -> Tuple[str, str]:
    """Extract text using EasyOCR"""
    import easyocr
    import numpy as np
    from PIL import Image
    import io as _io

    img = Image.open(_io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(img)

    reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    results = reader.readtext(img_array)

    # Sort by vertical position then horizontal (reading order)
    results_sorted = sorted(results, key=lambda r: (r[0][0][1], r[0][0][0]))
    text = "\n".join([res[1] for res in results_sorted if res[2] > 0.3])
    return text.strip(), "easyocr"
