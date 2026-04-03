"""
Document Service - Processing and Chunking.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Generator

from app.core.config import settings
from app.core.logging import get_logger
from app.services.vector.vector_store import (
    DocumentChunk,
    generate_document_id,
    generate_chunk_id,
)
from app.services.embedding.embedding_service import embedding_service

logger = get_logger(__name__)


@dataclass
class DocumentMetadata:
    document_id: str
    filename: str
    file_type: str
    file_size: int
    total_chunks: int
    uploaded_at: datetime
    document_type: Optional[str] = None
    summary: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "total_chunks": self.total_chunks,
            "uploaded_at": self.uploaded_at.isoformat(),
            "document_type": self.document_type,
            "summary": self.summary,
            "tags": self.tags,
        }


@dataclass
class IngestionResult:
    document_id: str
    metadata: DocumentMetadata
    chunks_created: int
    processing_time_ms: float
    status: str
    error: Optional[str] = None


class DocumentChunker:
    """Intelligent document chunking."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None,
        min_chunk_size: int = 100,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.overlap = overlap or settings.chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_text(
        self,
        text: str,
        document_id: str,
        metadata: Optional[dict] = None,
        strategy: str = "recursive",
    ) -> list[DocumentChunk]:
        """Chunk text into smaller pieces."""
        if not text or not text.strip():
            return []

        meta = metadata or {}

        if strategy == "recursive":
            raw_chunks = list(self._recursive_split(text))
        elif strategy == "sentence":
            raw_chunks = list(self._sentence_split(text))
        elif strategy == "paragraph":
            raw_chunks = list(self._paragraph_split(text))
        else:
            raw_chunks = list(self._recursive_split(text))

        chunks = []
        for idx, (start, end, content) in enumerate(raw_chunks):
            if len(content) >= self.min_chunk_size:
                chunk = DocumentChunk(
                    chunk_id=generate_chunk_id(document_id, idx),
                    content=content.strip(),
                    metadata={
                        "document_id": document_id,
                        "chunk_index": idx,
                        "total_chunks": len(raw_chunks),
                        "char_start": start,
                        "char_end": end,
                        **meta,
                    },
                )
                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        return chunks

    def _recursive_split(
        self, text: str
    ) -> Generator[tuple[int, int, str], None, None]:
        """Split text recursively by separators."""
        separators = ["\n\n\n", "\n\n", "\n", ". ", ", ", " "]

        def split_recursive(
            t: str, start: int = 0
        ) -> Generator[tuple[int, int, str], None, None]:
            if len(t) <= self.chunk_size:
                if len(t.strip()) >= self.min_chunk_size:
                    yield (start, start + len(t), t.strip())
                return

            best_pos = -1
            best_sep = ""

            for sep in separators:
                pos = t.rfind(sep, self.chunk_size // 2, self.chunk_size)
                if pos != -1:
                    best_pos = pos
                    best_sep = sep
                    break

            if best_pos == -1:
                best_pos = self.chunk_size
                best_sep = ""

            chunk = t[: best_pos + len(best_sep)]
            next_t = t[best_pos + len(best_sep) :]

            if chunk.strip():
                yield (start, start + len(chunk), chunk.strip())

            if next_t:
                overlap_start = max(0, best_pos - self.overlap)
                overlap_text = t[overlap_start : best_pos + len(best_sep)]
                yield from split_recursive(
                    overlap_text + next_t, start + len(chunk) - self.overlap
                )

        yield from split_recursive(text)

    def _sentence_split(self, text: str) -> Generator[tuple[int, int, str], None, None]:
        """Split text by sentences."""
        sentence_pattern = r"(?<=[.!?])\s+"
        sentences = re.split(sentence_pattern, text)

        current_chunk = ""
        current_start = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                if not current_chunk:
                    current_start = text.find(sentence)
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    yield (
                        current_start,
                        current_start + len(current_chunk),
                        current_chunk.strip(),
                    )
                current_chunk = sentence + " "
                current_start = text.find(sentence, current_start)

        if current_chunk.strip():
            yield (
                current_start,
                current_start + len(current_chunk),
                current_chunk.strip(),
            )

    def _paragraph_split(
        self, text: str
    ) -> Generator[tuple[int, int, str], None, None]:
        """Split text by paragraphs."""
        paragraphs = re.split(r"\n\s*\n", text)

        current = []
        current_start = 0
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_start = text.find(para, current_start)

            if current_length + len(para) <= self.chunk_size:
                if not current:
                    current_start = para_start
                current.append(para)
                current_length += len(para) + 2
            else:
                if current:
                    yield (current_start, para_start, "\n\n".join(current))

                if len(para) > self.chunk_size:
                    yield from self._recursive_split(para)
                    current_start = para_start + len(para)
                else:
                    current = [para]
                    current_start = para_start
                    current_length = len(para)

        if current:
            yield (
                current_start,
                current_start + len("\n\n".join(current)),
                "\n\n".join(current),
            )


class DocumentService:
    """Document processing and ingestion service."""

    def __init__(self):
        self.chunker = DocumentChunker()

    def process_document(
        self,
        text: str,
        filename: str,
        file_type: str,
        file_size: int,
        document_type: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        chunking_strategy: str = "recursive",
    ) -> IngestionResult:
        """Process and ingest a document."""
        from app.services.vector.vector_store import vector_store_service

        start_time = datetime.now()
        document_id = generate_document_id()

        meta = {
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "document_type": document_type,
            "summary": summary,
            "tags": tags or [],
            **(metadata or {}),
        }

        try:
            chunks = self.chunker.chunk_text(
                text=text,
                document_id=document_id,
                metadata=meta,
                strategy=chunking_strategy,
            )

            if not chunks:
                return IngestionResult(
                    document_id=document_id,
                    metadata=DocumentMetadata(
                        document_id=document_id,
                        filename=filename,
                        file_type=file_type,
                        file_size=file_size,
                        total_chunks=0,
                        uploaded_at=datetime.now(),
                    ),
                    chunks_created=0,
                    processing_time_ms=0,
                    status="failed",
                    error="No chunks generated",
                )

            texts = [c.content for c in chunks]
            vectors = embedding_service.generate_embeddings_batch(texts)

            for chunk, vector in zip(chunks, vectors):
                if vector:
                    chunk.vector = vector

            vector_store_service.upsert_chunks(chunks)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            doc_metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                total_chunks=len(chunks),
                uploaded_at=datetime.now(),
                document_type=document_type,
                summary=summary,
                tags=tags,
            )

            return IngestionResult(
                document_id=document_id,
                metadata=doc_metadata,
                chunks_created=len(chunks),
                processing_time_ms=processing_time,
                status="success",
            )

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return IngestionResult(
                document_id=document_id,
                metadata=DocumentMetadata(
                    document_id=document_id,
                    filename=filename,
                    file_type=file_type,
                    file_size=file_size,
                    total_chunks=0,
                    uploaded_at=datetime.now(),
                ),
                chunks_created=0,
                processing_time_ms=0,
                status="failed",
                error=str(e),
            )

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        from app.services.vector.vector_store import vector_store_service

        return vector_store_service.delete_by_document_id(document_id)


document_service = DocumentService()
