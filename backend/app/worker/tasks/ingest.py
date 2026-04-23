"""RAG Ingest Background Task - Celery"""

from celery import Task
from celery.result import AsyncResult

from app.worker import celery_app


@celery_app.task(bind=True, name="app.worker.tasks.ingest.ingest_to_rag")
def ingest_to_rag(
    self: Task,
    document_id: str,
    content: str,
    metadata: dict = None,
) -> AsyncResult:
    """Ingest document content to RAG system."""
    from app.services.rag.chunker import TextChunker
    from app.services.rag.embedder import EmbeddingService
    from app.services.vector.vector_store import VectorStoreService

    try:
        chunker = TextChunker()
        embedder = EmbeddingService()
        vector_store = VectorStoreService()

        self.update_state(
            state="PROCESSING",
            meta={"step": "Chunking text", "progress": 20},
        )

        chunks = chunker.chunk(content)

        self.update_state(
            state="PROCESSING",
            meta={"step": "Creating embeddings", "progress": 50},
        )

        for i, chunk in enumerate(chunks):
            embedding = embedder.generate_embedding(chunk)
            metadata_chunk = {
                "document_id": document_id,
                "chunk_index": i,
                **(metadata or {}),
            }

            self.update_state(
                state="PROCESSING",
                meta={
                    "step": f"Upserting chunk {i + 1}/{len(chunks)}",
                    "progress": 50 + (i * 50 // len(chunks)),
                },
            )

            vector_store.upsert(
                vectors=[embedding],
                ids=[f"{document_id}_chunk_{i}"],
                documents=[chunk],
                metadata=[metadata_chunk],
            )

        return {
            "document_id": document_id,
            "status": "success",
            "chunks_ingested": len(chunks),
        }

    except Exception as e:
        return {
            "document_id": document_id,
            "status": "failed",
            "error": str(e),
        }


@celery_app.task(bind=True, name="app.worker.tasks.ingest.delete_from_rag")
def delete_from_rag(self: Task, document_id: str) -> AsyncResult:
    """Delete document chunks from RAG system."""
    from app.services.vector.vector_store import VectorStoreService

    try:
        vector_store = VectorStoreService()
        vector_store.delete_by_filter({"document_id": document_id})

        return {
            "document_id": document_id,
            "status": "success",
        }

    except Exception as e:
        return {
            "document_id": document_id,
            "status": "failed",
            "error": str(e),
        }