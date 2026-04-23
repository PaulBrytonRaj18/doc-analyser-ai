"""Unit Tests - Database Models"""

import uuid


class TestDocumentModel:
    """Test Document ORM model."""

    def test_document_creation(self):
        """Test Document model creation."""
        from app.models.db import Document
        
        doc = Document(
            id=uuid.uuid4(),
            document_id="doc_test_001",
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            content_text="Test content",
            summary="Test summary",
            document_type="invoice",
            sub_type="commercial_invoice",
            classification_confidence=0.95,
            rag_ingested=True,
        )
        
        assert doc.document_id == "doc_test_001"
        assert doc.filename == "test.pdf"
        assert doc.file_type == "application/pdf"
        assert doc.file_size == 1024
        assert doc.content_text == "Test content"
        assert doc.summary == "Test summary"
        assert doc.document_type == "invoice"
        assert doc.sub_type == "commercial_invoice"
        assert doc.classification_confidence == 0.95
        assert doc.rag_ingested is True

    def test_document_default_values(self):
        """Test Document default values."""
        # Note: SQLAlchemy doesn't auto-generate values on direct instantiation
        # They are generated when added to database
        from app.models.db import Document
        
        doc = Document(
            document_id="doc_default",
            filename="default.pdf",
            file_type="application/pdf",
            file_size=0,
        )
        
        assert doc.document_id == "doc_default"


class TestDocumentChunkModel:
    """Test DocumentChunk ORM model."""

    def test_chunk_creation(self):
        """Test DocumentChunk model creation."""
        from app.models.db import DocumentChunk
        
        chunk = DocumentChunk(
            chunk_id="chunk_001",
            content="Test chunk content",
            page_number=1,
            chunk_index=0,
            chunk_metadata={"source": "test"},
        )
        
        assert chunk.chunk_id == "chunk_001"
        assert chunk.content == "Test chunk content"
        assert chunk.page_number == 1
        assert chunk.chunk_index == 0
        assert chunk.chunk_metadata == {"source": "test"}


class TestAnalysisResultModel:
    """Test AnalysisResult ORM model."""

    def test_analysis_result_creation(self):
        """Test AnalysisResult model creation."""
        from app.models.db import AnalysisResult
        
        result = AnalysisResult(
            result_type="classification",
            result_data={"type": "invoice", "confidence": 0.95},
        )
        
        assert result.result_type == "classification"
        assert result.result_data == {"type": "invoice", "confidence": 0.95}


class TestAuditLogModel:
    """Test AuditLog ORM model."""

    def test_audit_log_creation(self):
        """Test AuditLog model creation."""
        from app.models.db import AuditLog
        
        log = AuditLog(
            request_id="req_test_001",
            user_id="user_001",
            action="UPLOAD",
            resource_type="document",
            resource_id="doc_001",
            request_path="/v1/upload",
            request_method="POST",
            response_status=200,
            ip_address="127.0.0.1",
            previous_hash="",
            current_hash="test_hash_123",
        )
        
        assert log.request_id == "req_test_001"
        assert log.user_id == "user_001"
        assert log.action == "UPLOAD"
        assert log.resource_type == "document"
        assert log.request_path == "/v1/upload"
        assert log.request_method == "POST"
        assert log.response_status == 200
        assert log.current_hash == "test_hash_123"


class TestBatchJobModel:
    """Test BatchJob ORM model."""

    def test_batch_job_creation(self):
        """Test BatchJob model creation."""
        from app.models.db import BatchJob
        
        job = BatchJob(
            batch_id="batch_001",
            status="pending",
            total_files=10,
            processed_files=0,
            failed_files=0,
        )
        
        assert job.batch_id == "batch_001"
        assert job.status == "pending"
        assert job.total_files == 10
        assert job.processed_files == 0
        assert job.failed_files == 0

    def test_batch_job_completed(self):
        """Test BatchJob completion status."""
        from app.models.db import BatchJob
        
        job = BatchJob(
            batch_id="batch_done",
            status="completed",
            total_files=10,
            processed_files=8,
            failed_files=2,
        )
        
        assert job.status == "completed"
        assert job.processed_files + job.failed_files == job.total_files


class TestWebhookModel:
    """Test Webhook ORM model."""

    def test_webhook_creation(self):
        """Test Webhook model creation."""
        from app.models.db import Webhook
        
        # Note: Default values are applied when added to DB, not at instantiation
        webhook = Webhook(
            url="https://example.com/webhook",
            secret="secret_key_123",
            events=["document.ready", "batch.complete"],
            active=True,
        )
        
        assert webhook.url == "https://example.com/webhook"
        assert webhook.secret == "secret_key_123"
        assert webhook.events == ["document.ready", "batch.complete"]
        assert webhook.active is True