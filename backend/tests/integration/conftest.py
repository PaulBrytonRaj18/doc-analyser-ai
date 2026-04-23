"""
Integration Test Configuration - DocuLens AI v4.0
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("CELERY_ENABLED", "false")
os.environ.setdefault("PINECONE_API_KEY", "")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    from app.main import app
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_image_bytes() -> bytes:
    """Create mock image bytes for testing."""
    import io
    from PIL import Image
    
    img = Image.new('RGB', (100, 100), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def mock_pdf_bytes() -> bytes:
    """Create mock PDF bytes for testing."""
    return b"%PDF-1.4 mock pdf content"


@pytest.fixture
def mock_vector_search_result():
    """Mock vector search result."""
    from dataclasses import dataclass
    
    @dataclass
    class MockSearchResult:
        result_id: str = "test_result_1"
        content: str = "This is test document content about payment terms and invoices."
        score: float = 0.95
        metadata: dict = None
        
        def __post_init__(self):
            if self.metadata is None:
                self.metadata = {
                    "document_id": "doc_test_001",
                    "filename": "test_invoice.pdf",
                    "page": 1,
                    "chunk_index": 0,
                }
    
    return [
        MockSearchResult(
            result_id="result_1",
            content="Invoice payment terms: Net 30 days. Amount due: $1,500.00",
            score=0.92,
            metadata={"document_id": "doc_001", "filename": "invoice1.pdf", "page": 1},
        ),
        MockSearchResult(
            result_id="result_2",
            content="Late payment fee: 1.5% per month after due date.",
            score=0.88,
            metadata={"document_id": "doc_001", "filename": "invoice1.pdf", "page": 2},
        ),
    ]


@pytest.fixture
def mock_embedding():
    """Mock embedding vector."""
    return [0.1] * 384


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    from dataclasses import dataclass
    
    @dataclass
    class MockLLMResponse:
        content: str = "Based on the documents, the payment terms are Net 30 days with a 1.5% late fee."
        model: str = "gpt-4"
        usage: dict = None
        
        def __post_init__(self):
            if self.usage is None:
                self.usage = {"prompt_tokens": 100, "completion_tokens": 50}
    
    return MockLLMResponse()