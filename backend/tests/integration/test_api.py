"""
API Integration Tests - DocuLens AI v4.0
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health endpoint returns healthy status."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "features" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns service info."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "health" in data


class TestRAGEndpoint:
    """Tests for RAG query endpoint."""

    @pytest.mark.asyncio
    async def test_rag_search_no_results(self, client: AsyncClient):
        """Test RAG search with no matching documents."""
        with patch("app.services.embedding.embedding_service.embedding_service.generate_embedding", return_value=[0.1] * 384):
            with patch("app.services.vector.vector_store.vector_store_service.search_similar", return_value=[]):
                response = await client.post(
                    "/v1/rag/search",
                    json={"query": "test query", "top_k": 5},
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 0
                assert data["results"] == []

    @pytest.mark.asyncio
    async def test_rag_query_with_mock(self, client: AsyncClient, mock_llm_response):
        """Test RAG query endpoint with mocked services."""
        with patch("app.services.embedding.embedding_service.embedding_service.generate_embedding", return_value=[0.1] * 384):
            with patch("app.services.vector.vector_store.vector_store_service.search_similar", return_value=[]):
                with patch("app.services.llm.llm_service.llm_service.generate", return_value=mock_llm_response):
                    response = await client.post(
                        "/v1/rag/query",
                        json={"query": "What are the payment terms?"},
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "answer" in data
                    assert "sources" in data

    @pytest.mark.asyncio
    async def test_rag_query_no_results(self, client: AsyncClient):
        """Test RAG query returns message when no results found."""
        with patch("app.services.embedding.embedding_service.embedding_service.generate_embedding", return_value=[0.1] * 384):
            with patch("app.services.vector.vector_store.vector_store_service.search_similar", return_value=[]):
                response = await client.post(
                    "/v1/rag/query",
                    json={"query": "nonexistent topic xyz"},
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["answer"] == "No relevant documents found for your query."

    @pytest.mark.asyncio
    async def test_rag_search_with_results(self, client: AsyncClient, mock_vector_search_result):
        """Test RAG search with mock results."""
        with patch("app.services.embedding.embedding_service.embedding_service.generate_embedding", return_value=[0.1] * 384):
            with patch("app.services.vector.vector_store.vector_store_service.search_similar", return_value=mock_vector_search_result):
                response = await client.post(
                    "/v1/rag/search",
                    json={"query": "payment terms", "top_k": 5},
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 2
                assert len(data["results"]) == 2


class TestUploadEndpoint:
    """Tests for upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_file_failed_processing(self, client: AsyncClient, mock_pdf_bytes: bytes):
        """Test upload with failed processing returns error."""
        mock_file_result = MagicMock()
        mock_file_result.status = "failed"
        mock_file_result.error = "Unsupported file format"
        
        with patch("app.services.processing.file_processor.FileProcessor.process_file", return_value=mock_file_result):
            response = await client.post(
                "/v1/upload",
                files={"file": ("test.xyz", mock_pdf_bytes, "application/octet-stream")},
            )
            
            assert response.status_code == 400