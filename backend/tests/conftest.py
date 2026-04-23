"""
Pytest Configuration and Fixtures - DocuLens AI v4.0
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Generator

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment before imports
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("CELERY_ENABLED", "false")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_text() -> str:
    """Sample document text for testing."""
    return """
    Invoice #INV-2024-0091
    Date: March 5, 2024
    
    From: Acme Corp
    To: Tech Inc
    
    Description: Software licensing services
    Amount: $12,400.00
    Due: April 4, 2024
    
    Payment terms: Net 30 days
    Late fee: 1.5% per month
    
    Contact: billing@acmecorp.com
    """


@pytest.fixture
def sample_entities() -> dict:
    """Expected entities from sample text."""
    return {
        "invoice_numbers": ["INV-2024-0091"],
        "organizations": ["Acme Corp", "Tech Inc"],
        "dates": ["March 5, 2024", "April 4, 2024"],
        "monetary_values": ["$12,400.00"],
        "email_addresses": ["billing@acmecorp.com"],
    }


@pytest.fixture
def sample_document() -> dict:
    """Sample document metadata."""
    return {
        "document_id": "doc_test_001",
        "filename": "test_invoice.pdf",
        "file_type": "application/pdf",
        "file_size": 1024,
        "content_text": "Test invoice content",
        "document_type": "invoice",
        "summary": "Test summary",
    }


@pytest.fixture
def sample_chunk() -> dict:
    """Sample text chunk."""
    return {
        "chunk_id": "chunk_001",
        "content": "This is a sample document chunk for testing RAG functionality.",
        "document_id": "doc_test_001",
        "chunk_index": 0,
    }


@pytest.fixture
def sample_chunks() -> list[str]:
    """Sample text chunks for testing."""
    return [
        "First chunk about machine learning and AI models.",
        "Second chunk discussing neural networks architecture.",
        "Third chunk covering optimization algorithms.",
        "Fourth chunk about training data preparation.",
        "Fifth chunk related to model evaluation metrics.",
    ]


@pytest.fixture
def sample_query() -> str:
    """Sample RAG query."""
    return "What are the payment terms in this invoice?"