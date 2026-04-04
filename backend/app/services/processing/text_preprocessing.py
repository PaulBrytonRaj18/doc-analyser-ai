"""
Preprocessing Service for text cleaning and semantic chunking.
"""

import re
from typing import List

from app.core.logging import get_logger

logger = get_logger(__name__)


class TextPreprocessor:
    """Clean and normalize document text."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        text = re.sub(r"\r\n", "\n", text)

        text = re.sub(r"[ \t]+", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)

        text = text.strip()

        return text

    @staticmethod
    def remove_noise(text: str) -> str:
        """Remove common noise patterns."""
        text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)

        text = re.sub(r"Source:.*", "", text, flags=re.IGNORECASE)

        text = re.sub(r"\[IMAGE\]|\[FIGURE\]|\[TABLE\]", "", text, flags=re.IGNORECASE)

        text = re.sub(r"http[s]?://\S+", "", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()


class SemanticChunker:
    """Chunk text with semantic awareness."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks."""
        if not text:
            return []

        text = TextPreprocessor.clean_text(text)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        if not paragraphs:
            paragraphs = [text]

        chunks = []
        current_chunk = ""
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if para_size > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                    current_size = 0

                chunks.extend(self._split_large_paragraph(para))
                continue

            if current_size + para_size > self.chunk_size and current_chunk:
                chunks.append(current_chunk)

                overlap_start = max(0, len(current_chunk) - self.overlap)
                overlap_text = current_chunk[overlap_start:]
                current_chunk = overlap_text + para + "\n\n"
                current_size = len(current_chunk)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                current_size += para_size

        if current_chunk:
            chunks.append(current_chunk)

        return [c.strip() for c in chunks if c.strip()]

    def _split_large_paragraph(self, text: str) -> List[str]:
        """Split a large paragraph into smaller chunks."""
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current = ""

        for sent in sentences:
            if len(current) + len(sent) > self.chunk_size:
                if current:
                    chunks.append(current)
                current = sent
            else:
                current += " " + sent if current else sent

        if current:
            chunks.append(current)

        return chunks


text_preprocessor = TextPreprocessor()
semantic_chunker = SemanticChunker()
