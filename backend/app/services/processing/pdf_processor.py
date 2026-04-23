"""
PDF Processing Service using PyMuPDF and pdfplumber.
"""

import io
from typing import Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import for optional dependencies
_fitz = None
_pdfplumber = None


def _get_fitz():
    global _fitz
    if _fitz is None:
        try:
            import fitz

            _fitz = fitz
        except ImportError:
            logger.warning("PyMuPDF not installed. PDF processing may be limited.")
            _fitz = False
    return _fitz


def _get_pdfplumber():
    global _pdfplumber
    if _pdfplumber is None:
        try:
            import pdfplumber

            _pdfplumber = pdfplumber
        except ImportError:
            logger.warning("pdfplumber not installed.")
            _pdfplumber = False
    return _pdfplumber


class PDFProcessor:
    """Extract text and structure from PDF files."""

    def extract_text(
        self, file_bytes: bytes, preserve_layout: bool = True
    ) -> Tuple[str, dict]:
        """Extract text from PDF with optional layout preservation."""
        metadata = {"num_pages": 0, "file_type": "pdf", "has_tables": False}
        full_text = ""

        fitz_lib = _get_fitz()
        if fitz_lib:
            try:
                with fitz_lib.open(stream=file_bytes) as doc:
                    metadata["num_pages"] = len(doc)

                    if preserve_layout:
                        full_text = self._extract_with_pymupdf_layout(doc)
                    else:
                        full_text = self._extract_simple(doc)

            except Exception as e:
                logger.warning(f"PyMuPDF failed, trying pdfplumber: {e}")
                try:
                    full_text, metadata = self._extract_with_pdfplumber(file_bytes)
                except Exception as e2:
                    logger.error(f"PDF extraction failed completely: {e2}")
                    return "", metadata
        else:
            pdfplumber_lib = _get_pdfplumber()
            if pdfplumber_lib:
                try:
                    full_text, metadata = self._extract_with_pdfplumber(file_bytes)
                except Exception as e2:
                    logger.error(f"PDF extraction failed: {e2}")
                    return "", metadata

        return full_text, metadata

    def _extract_with_pymupdf_layout(self, doc) -> str:
        """Extract text maintaining paragraph and heading structure."""
        text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                text_parts.append(text)

        return "\n\n".join(text_parts)

    def _extract_simple(self, doc) -> str:
        """Simple text extraction."""
        return "\n\n".join([page.get_text() for page in doc])

    def _extract_with_pdfplumber(self, file_bytes: bytes) -> Tuple[str, dict]:
        """Fallback extraction using pdfplumber."""
        metadata = {"num_pages": 0, "file_type": "pdf", "has_tables": False}
        text_parts = []

        pdfplumber_lib = _get_pdfplumber()
        if not pdfplumber_lib:
            return "", metadata

        try:
            with pdfplumber_lib.open(io.BytesIO(file_bytes)) as pdf:
                metadata["num_pages"] = len(pdf.pages)

                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                    if page.extract_tables():
                        metadata["has_tables"] = True

            return "\n\n".join(text_parts), metadata
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return "", metadata

    def extract_metadata(self, file_bytes: bytes) -> dict:
        """Extract PDF metadata (author, title, etc)."""
        fitz_lib = _get_fitz()
        if not fitz_lib:
            return {}

        try:
            with fitz_lib.open(stream=file_bytes, doc_type="pdf") as doc:
                meta = doc.metadata
                return {
                    "title": meta.get("title", ""),
                    "author": meta.get("author", ""),
                    "subject": meta.get("subject", ""),
                    "creator": meta.get("creator", ""),
                    "producer": meta.get("producer", ""),
                    "num_pages": len(doc),
                }
        except Exception as e:
            logger.error(f"Failed to extract PDF metadata: {e}")
            return {}


pdf_processor = PDFProcessor()
