"""
Vector Store Service - Pinecone Integration (Optional).
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List
from uuid import uuid4

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import for optional dependencies
_pinecone = None


def _get_pinecone():
    global _pinecone
    if _pinecone is None:
        try:
            from pinecone import Pinecone, ServerlessSpec

            _pinecone = (Pinecone, ServerlessSpec)
        except ImportError:
            logger.warning("Pinecone not installed. RAG features will be disabled.")
            _pinecone = False
    return _pinecone


@dataclass
class DocumentChunk:
    chunk_id: str
    content: str
    metadata: dict = field(default_factory=dict)
    vector: Optional[list[float]] = None


@dataclass
class SearchResult:
    result_id: str
    score: float
    content: str
    metadata: dict


class VectorStoreService:
    """Pinecone vector database service."""

    def __init__(self):
        self._client = None
        self._index = None
        self._initialized = False
        self._available = None

    @property
    def is_available(self) -> bool:
        if self._available is None:
            pinecone_lib = _get_pinecone()
            self._available = pinecone_lib is not False and bool(
                settings.pinecone_api_key
            )
        return self._available

    @property
    def client(self):
        if not self.is_available:
            return None
        if self._client is None:
            Pinecone, _ = _get_pinecone()
            self._client = Pinecone(api_key=settings.pinecone_api_key)
        return self._client

    def initialize(self, force_recreate: bool = False) -> bool:
        """Initialize or connect to Pinecone index."""
        if not self.is_available:
            logger.warning("Vector store not available. RAG features disabled.")
            return False

        if self._initialized and not force_recreate:
            return True

        try:
            existing_indexes = [idx.name for idx in self.client.list_indexes()]

            if settings.pinecone_index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {settings.pinecone_index_name}")
                self._create_index()
            else:
                logger.info(
                    f"Connecting to existing index: {settings.pinecone_index_name}"
                )

            self._index = self.client.Index(settings.pinecone_index_name)
            self._initialized = True

            return True

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            return False

    def _create_index(self) -> None:
        """Create a new Pinecone index."""
        dimension = self._get_embedding_dimension()
        _, ServerlessSpec = _get_pinecone()

        self.client.create_index(
            name=settings.pinecone_index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud, region=settings.pinecone_region
            ),
        )
        logger.info(
            f"Created index '{settings.pinecone_index_name}' with dimension {dimension}"
        )

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension based on provider."""
        if settings.embedding_provider == "gemini":
            return 768
        elif settings.embedding_provider == "openai":
            return 1536
        return 384

    def upsert_chunks(self, chunks: List[DocumentChunk], namespace: str = "") -> dict:
        """Insert document chunks into vector store."""
        if not self.is_available:
            logger.warning("Vector store not available, skipping upsert")
            return {"success": 0, "failed": 0}

        if not self._index:
            self.initialize()

        vectors = []
        success_count = 0

        for chunk in chunks:
            if chunk.vector:
                vectors.append(
                    {
                        "id": chunk.chunk_id,
                        "values": chunk.vector,
                        "metadata": {
                            "content": chunk.content[:10000],
                            "content_length": len(chunk.content),
                            **chunk.metadata,
                        },
                    }
                )

        if vectors:
            self._index.upsert(vectors=vectors, namespace=namespace)
            success_count = len(vectors)

        logger.info(f"Upserted {success_count} chunks to vector store")
        return {"success": success_count, "failed": 0}

    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        filters: Optional[dict] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        if not self.is_available:
            return []

        if not self._index:
            self.initialize()

        try:
            response = self._index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filters,
                include_values=True,
                include_metadata=True,
            )

            return [
                SearchResult(
                    result_id=match.id,
                    score=match.score,
                    content=match.metadata.get("content", ""),
                    metadata=match.metadata,
                )
                for match in response.matches
            ]

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def delete_by_document_id(self, document_id: str, namespace: str = "") -> bool:
        """Delete all vectors for a document."""
        if not self.is_available:
            return False

        if not self._index:
            self.initialize()

        try:
            self._index.delete(
                filter={"document_id": {"$eq": document_id}}, namespace=namespace
            )
            logger.info(f"Deleted vectors for document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False

    def delete_all(self, namespace: str = "") -> bool:
        """Delete all vectors in namespace."""
        if not self.is_available:
            return False

        if not self._index:
            self.initialize()

        try:
            self._index.delete(delete_all=True, namespace=namespace)
            logger.warning(f"Deleted all vectors in namespace: '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete all vectors: {e}")
            return False

    def get_statistics(self) -> dict:
        """Get index statistics."""
        if not self.is_available:
            return {"total_vectors": 0, "dimension": 0, "index_full": False}

        if not self._index:
            self.initialize()

        stats = self._index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_full": stats.index_full,
        }


def generate_document_id() -> str:
    """Generate unique document ID."""
    return f"doc_{uuid4().hex[:12]}"


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """Generate unique chunk ID."""
    return f"{document_id}_chunk_{chunk_index:04d}"


vector_store_service = VectorStoreService()
