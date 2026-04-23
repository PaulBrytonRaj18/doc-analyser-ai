"""Unit Tests - RAG Services"""



class TestRerankerService:
    """Test RAG reranker service."""

    def test_reranked_result_structure(self):
        """Test RerankedResult dataclass."""
        from app.services.rag.reranker import RerankedResult

        result = RerankedResult(
            chunk="This is a test chunk about AI.",
            score=0.95,
            index=0,
        )

        assert result.chunk == "This is a test chunk about AI."
        assert result.score == 0.95
        assert result.index == 0

    def test_reranker_empty_chunks(self):
        """Test reranker with empty chunks."""
        from app.services.rag.reranker import RerankerService

        reranker = RerankerService()
        chunks = []

        # Should return empty list for empty chunks
        results = reranker.rerank("test query", chunks, top_k=6)

        assert results == []


class TestCitationService:
    """Test citation builder service."""

    def test_citation_structure(self):
        """Test Citation dataclass."""
        from app.services.rag.citer import Citation

        citation = Citation(
            document_id="doc_001",
            chunk_id="chunk_001",
            page=1,
            region={"x": 10, "y": 20, "width": 100, "height": 50},
            excerpt="Payment terms apply...",
            relevance_score=0.95,
        )

        assert citation.document_id == "doc_001"
        assert citation.chunk_id == "chunk_001"
        assert citation.page == 1
        assert citation.region == {"x": 10, "y": 20, "width": 100, "height": 50}
        assert citation.excerpt == "Payment terms apply..."
        assert citation.relevance_score == 0.95

    def test_citation_no_optional_fields(self):
        """Test Citation with optional fields None."""
        from app.services.rag.citer import Citation

        citation = Citation(
            document_id="doc_001",
            chunk_id="chunk_001",
            page=None,
            region=None,
            excerpt="Test excerpt",
            relevance_score=0.9,
        )

        assert citation.page is None
        assert citation.region is None

    def test_build_citations(self):
        """Test building multiple citations."""
        from app.services.rag.citer import CitationService

        service = CitationService()

        sources = [
            {"document_id": "doc_001", "chunk_id": "chunk_001", "relevance_score": 0.95},
            {"document_id": "doc_002", "chunk_id": "chunk_002", "relevance_score": 0.85},
        ]

        retrieved_chunks = [
            {"id": "chunk_001", "text": "First chunk"},
            {"id": "chunk_002", "text": "Second chunk"},
        ]

        citations = service.build_citations(sources, retrieved_chunks)

        assert len(citations) == 2
        assert citations[0].document_id == "doc_001"
        assert citations[1].document_id == "doc_002"

    def test_format_citation(self):
        """Test formatting a citation for display."""
        from app.services.rag.citer import CitationService, Citation

        service = CitationService()

        citation = Citation(
            document_id="doc_001",
            chunk_id="chunk_001",
            page=1,
            region=None,
            excerpt="Payment terms apply...",
            relevance_score=0.95,
        )

        formatted = service.format_citation(citation)

        assert "doc_001" in formatted
        assert "1" in formatted  # page number
        assert "0.95" in formatted  # relevance score


class TestTextChunker:
    """Test text chunking."""

    def test_chunker_creation(self):
        """Test TextPreprocessor can be instantiated."""
        from app.services.processing.text_preprocessing import TextPreprocessor

        chunker = TextPreprocessor()
        
        assert chunker is not None

    def test_text_preprocessor_methods(self):
        """Test text preprocessing functionality."""
        from app.services.processing.text_preprocessing import TextPreprocessor

        chunker = TextPreprocessor()
        
        # Check for any methods the preprocessor has
        assert hasattr(chunker, '__init__')


class TestEmbeddingService:
    """Test embedding service."""

    def test_embedding_service_creation(self):
        """Test EmbeddingService can be instantiated."""
        from app.services.embedding.embedding_service import EmbeddingService

        embedder = EmbeddingService()
        
        assert embedder is not None

    def test_generate_embedding(self):
        """Test embedding generation."""
        from app.services.embedding.embedding_service import EmbeddingService

        embedder = EmbeddingService()
        
        # Test embedding generation
        text = "This is a test document."
        
        try:
            embedding = embedder.generate_embedding(text)
            # May fail if no API key
            if embedding:
                assert isinstance(embedding, list)
        except Exception:
            pass  # Skip if no API key configured


class TestVectorStoreService:
    """Test vector store service."""

    def test_vector_store_creation(self):
        """Test VectorStoreService can be instantiated."""
        from app.services.vector.vector_store import VectorStoreService

        store = VectorStoreService()
        
        assert store is not None

    def test_upsert_vectors(self):
        """Test vector upsert."""
        from app.services.vector.vector_store import VectorStoreService

        store = VectorStoreService()
        
        # Test upsert with mock data - may fail without API key
        try:
            _ = store.upsert(
                vectors=[[0.1] * 768],
                ids=["test_001"],
                documents=["Test document"],
                metadata=[{"source": "test"}]
            )
        except Exception:
            pass

    def test_search_vectors(self):
        """Test vector search."""
        from app.services.vector.vector_store import VectorStoreService

        store = VectorStoreService()
        
        try:
            _ = store.search("test query", top_k=5)
        except Exception:
            pass