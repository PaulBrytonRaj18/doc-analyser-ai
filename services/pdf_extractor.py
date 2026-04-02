"""
PDF text extraction using PyMuPDF (fitz)
Preserves layout and handles complex PDFs
"""

import io
from typing import Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from PDF bytes.
    Returns (extracted_text, page_count)
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts = []
        page_count = len(doc)

        for page_num in range(page_count):
            page = doc[page_num]

            # Try text extraction with layout preservation
            text = page.get_text("text")
            if text.strip():
                texts.append(f"[Page {page_num + 1}]\n{text.strip()}")
            else:
                # Fallback: try dict mode for better structure
                blocks = page.get_text("dict")["blocks"]
                page_text = []
                for block in blocks:
                    if block.get("type") == 0:  # text block
                        for line in block.get("lines", []):
                            line_text = " ".join(
                                span["text"] for span in line.get("spans", [])
                            )
                            if line_text.strip():
                                page_text.append(line_text)
                if page_text:
                    texts.append(f"[Page {page_num + 1}]\n" + "\n".join(page_text))

        doc.close()

        full_text = "\n\n".join(texts)
        logger.info(f"PDF extracted: {page_count} pages, {len(full_text)} chars")
        return full_text, page_count

    except ImportError:
        logger.warning("PyMuPDF not available, trying pdfplumber")
        return _extract_with_pdfplumber(file_bytes)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def _extract_with_pdfplumber(file_bytes: bytes) -> Tuple[str, int]:
    """Fallback PDF extraction using pdfplumber"""
    try:
        import pdfplumber

        texts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    texts.append(f"[Page {i + 1}]\n{text.strip()}")

        full_text = "\n\n".join(texts)
        logger.info(f"pdfplumber extracted: {page_count} pages, {len(full_text)} chars")
        return full_text, page_count

    except Exception as e:
        logger.error(f"pdfplumber extraction error: {e}")
        raise ValueError(f"PDF extraction failed: {str(e)}")
