"""
Embedding Service - Multi-Provider Support (Gemini, OpenAI, Local).
"""

import hashlib
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import for optional dependencies
try:
    import numpy as np  # noqa: F401

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not installed. Embedding features may be limited.")


class EmbeddingService:
    """Multi-provider embedding service."""

    def __init__(self):
        self._gemini_client = None
        self._openai_client = None
        self._local_model = None

    def _get_gemini_client(self):
        """Get or initialize Gemini client."""
        if self._gemini_client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self._gemini_client = genai
            except ImportError:
                logger.error("Google Generative AI not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        return self._gemini_client

    def _get_openai_client(self):
        """Get or initialize OpenAI client."""
        if self._openai_client is None and settings.openai_api_key:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.error("OpenAI not installed")
        return self._openai_client

    def _get_local_model(self):
        """Get or initialize local embedding model."""
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._local_model = SentenceTransformer(settings.local_embedding_model)
                logger.info(
                    f"Loaded local embedding model: {settings.local_embedding_model}"
                )
            except ImportError:
                logger.error("sentence-transformers not installed")
        return self._local_model

    def generate_embedding(
        self, text: str, use_cache: bool = True
    ) -> Optional[list[float]]:
        """Generate embedding for text."""
        if not text:
            return None

        cache_key = self._get_cache_key(text)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        embedding = None

        if settings.embedding_provider == "gemini":
            embedding = self._generate_gemini_embedding(text)
        elif settings.embedding_provider == "openai":
            embedding = self._generate_openai_embedding(text)
        elif settings.embedding_provider == "local":
            embedding = self._generate_local_embedding(text)

        if embedding:
            self._save_to_cache(cache_key, embedding)

        return embedding

    def generate_embeddings_batch(
        self, texts: list[str], use_cache: bool = True, batch_size: int = 100
    ) -> list[Optional[list[float]]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        embeddings = []
        texts_to_embed = []
        indices_to_embed = []

        for idx, text in enumerate(texts):
            if not text:
                embeddings.append(None)
                continue

            cache_key = self._get_cache_key(text)

            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached:
                    embeddings.append(cached)
                    continue

            texts_to_embed.append(text)
            indices_to_embed.append(idx)
            embeddings.append(None)

        if texts_to_embed:
            batch_embeddings = self._generate_batch_embeddings(
                texts_to_embed, batch_size
            )

            for idx, embedding, text in zip(
                indices_to_embed, batch_embeddings, texts_to_embed
            ):
                embeddings[idx] = embedding
                if embedding and use_cache:
                    self._save_to_cache(self._get_cache_key(text), embedding)

        return embeddings

    def _generate_gemini_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding using Gemini."""
        try:
            client = self._get_gemini_client()
            if not client:
                return None

            result = client.embed_content(model="models/embedding-001", content=text)
            return result["embedding"]

        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            return None

    def _generate_openai_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding using OpenAI."""
        try:
            client = self._get_openai_client()
            if not client:
                return None

            response = client.embeddings.create(
                model=settings.openai_embedding_model, input=text
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return None

    def _generate_local_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding using local model."""
        try:
            model = self._get_local_model()
            if not model:
                return None

            return model.encode(text).tolist()

        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            return None

    def _generate_batch_embeddings(
        self, texts: list[str], batch_size: int
    ) -> list[Optional[list[float]]]:
        """Generate embeddings in batches."""
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            if settings.embedding_provider == "gemini":
                batch_results = [self._generate_gemini_embedding(t) for t in batch]
            elif settings.embedding_provider == "openai":
                batch_results = self._generate_openai_batch(batch)
            else:
                batch_results = self._generate_local_batch(batch)

            results.extend(batch_results)

        return results

    def _generate_openai_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Generate OpenAI embeddings in batch."""
        try:
            client = self._get_openai_client()
            if not client:
                return [None] * len(texts)

            response = client.embeddings.create(
                model=settings.openai_embedding_model, input=texts
            )
            return [item.embedding for item in response.data]

        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            return [None] * len(texts)

    def _generate_local_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Generate local embeddings in batch."""
        try:
            model = self._get_local_model()
            if not model:
                return [None] * len(texts)

            return model.encode(texts).tolist()

        except Exception as e:
            logger.error(f"Local batch embedding failed: {e}")
            return [None] * len(texts)

    def compute_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not NUMPY_AVAILABLE:
            return 0.0
        try:
            import numpy as np

            v1 = np.array(vec1)
            v2 = np.array(vec2)

            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(np.dot(v1, v2) / (norm1 * norm2))
        except Exception:
            return 0.0

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return f"emb:{hashlib.sha256(text.encode()).hexdigest()[:32]}"

    def _get_from_cache(self, key: str) -> Optional[list[float]]:
        """Get embedding from cache."""
        try:
            from app.services.cache import cache_service

            cached = cache_service.get(key)
            if cached:
                return [float(x) for x in cached]
        except Exception:
            pass
        return None

    def _save_to_cache(self, key: str, embedding: list[float]) -> None:
        """Save embedding to cache."""
        try:
            from app.services.cache import cache_service

            cache_service.set(key, embedding, ttl=86400 * 30)
        except Exception:
            pass


embedding_service = EmbeddingService()
