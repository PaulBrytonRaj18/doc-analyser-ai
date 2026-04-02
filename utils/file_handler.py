"""
Utility functions for file handling, type detection, and validation.
"""

import os
import magic  # python-magic for MIME detection
from typing import Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

# Supported MIME types
SUPPORTED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "docx",
    "image/jpeg": "image",
    "image/jpg": "image",
    "image/png": "image",
    "image/tiff": "image",
    "image/bmp": "image",
    "image/webp": "image",
    "image/gif": "image",
}

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def detect_file_type(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Detect file type from content (magic bytes) and filename.
    Returns (file_type, mime_type)
    """
    try:
        mime = magic.from_buffer(file_bytes[:2048], mime=True)
        if mime in SUPPORTED_TYPES:
            return SUPPORTED_TYPES[mime], mime
    except Exception as e:
        logger.warning(f"python-magic detection failed: {e}, falling back to extension")

    # Fallback: use file extension
    ext = os.path.splitext(filename.lower())[1].lstrip(".")
    ext_map = {
        "pdf": ("pdf", "application/pdf"),
        "docx": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "doc": ("docx", "application/msword"),
        "jpg": ("image", "image/jpeg"),
        "jpeg": ("image", "image/jpeg"),
        "png": ("image", "image/png"),
        "tiff": ("image", "image/tiff"),
        "tif": ("image", "image/tiff"),
        "bmp": ("image", "image/bmp"),
        "webp": ("image", "image/webp"),
        "gif": ("image", "image/gif"),
    }
    if ext in ext_map:
        return ext_map[ext]

    return "unknown", "application/octet-stream"


def validate_file(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate file size and type.
    Returns (is_valid, error_message)
    """
    if len(file_bytes) == 0:
        return False, "File is empty"

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        return False, f"File too large: {size_mb:.1f}MB (max {MAX_FILE_SIZE_MB}MB)"

    file_type, mime_type = detect_file_type(file_bytes, filename)
    if file_type == "unknown":
        return False, f"Unsupported file type. Accepted: PDF, DOCX, JPG, PNG, TIFF, BMP, WEBP"

    return True, ""


def count_words(text: str) -> int:
    """Count words in extracted text."""
    if not text:
        return 0
    return len(text.split())
