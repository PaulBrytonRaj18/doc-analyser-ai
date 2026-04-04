"""
Unified File Processing Service.
Handles PDF, DOCX, and Image files.
"""

import io
import hashlib
import mimetypes
from typing import Tuple, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.processing.pdf_processor import pdf_processor
from app.services.processing.docx_processor import docx_processor
from app.services.processing.image_processor import image_processor

logger = get_logger(__name__)


class FileProcessingError(Exception):
    """Custom exception for file processing errors."""

    pass


class FileProcessor:
    """Unified file processor for all supported document types."""

    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/octet-stream": None,  # Will be detected from filename
        "image/png": "image",
        "image/jpeg": "image",
        "image/jpg": "image",
        "image/tiff": "image",
        "image/bmp": "image",
    }

    # File extension to MIME type mapping
    EXTENSION_MIME_MAP = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
        ".bmp": "image/bmp",
    }

    def __init__(self):
        self.pdf = pdf_processor
        self.docx = docx_processor
        self.image = image_processor

    def process_file(
        self,
        file_bytes: bytes,
        content_type: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Tuple[str, dict]:
        """Process a file and extract text based on file type."""
        detected_type = content_type or self._detect_type(filename, file_bytes)

        if not detected_type:
            raise FileProcessingError("Unable to detect file type")

        file_format = self.SUPPORTED_TYPES.get(detected_type)

        if not file_format:
            detected_type = self._detect_from_filename(filename)
            file_format = self.SUPPORTED_TYPES.get(detected_type)

        if not file_format:
            raise FileProcessingError(f"Unsupported file type: {detected_type}")

        logger.info(f"Processing {file_format} file: {filename}")

        if file_format == "pdf":
            return self.pdf.extract_text(file_bytes, preserve_layout=True)
        elif file_format == "docx":
            return self.docx.extract_text(file_bytes)
        elif file_format == "image":
            return self.image.extract_text(file_bytes)
        else:
            raise FileProcessingError(f"Unhandled file format: {file_format}")

    def _detect_from_filename(self, filename: Optional[str]) -> Optional[str]:
        """Detect MIME type from filename extension."""
        if not filename:
            return None
        import os

        _, ext = os.path.splitext(filename.lower())
        return self.EXTENSION_MIME_MAP.get(ext)

    def _detect_type(self, filename: Optional[str], file_bytes: bytes) -> Optional[str]:
        """Detect file type from filename or content."""
        detected = self._detect_from_filename(filename)
        if detected and detected in self.SUPPORTED_TYPES:
            return detected

        if filename:
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type and mime_type in self.SUPPORTED_TYPES:
                return mime_type

        magic_bytes = file_bytes[:16]

        if magic_bytes.startswith(b"%PDF"):
            return "application/pdf"
        elif magic_bytes.startswith(b"PK\x03\x04"):
            return self._detect_from_filename(filename) or "application/octet-stream"

        try:
            from PIL import Image

            Image.open(io.BytesIO(file_bytes))
            return "image/jpeg"
        except Exception:
            pass

        return None

    def validate_file(self, file_bytes: bytes, content_type: Optional[str]) -> bool:
        """Validate file size and type."""
        if len(file_bytes) > settings.max_file_size_bytes:
            raise FileProcessingError(
                f"File too large. Max size: {settings.max_file_size_mb}MB"
            )

        if content_type and content_type not in self.SUPPORTED_TYPES:
            detected = self._detect_from_filename(None)
            if not detected:
                raise FileProcessingError(f"Unsupported file type: {content_type}")

        return True


file_processor = FileProcessor()
