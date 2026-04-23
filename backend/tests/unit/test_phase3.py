"""Unit Tests - Phase 3 Services"""



class TestRedactorService:
    """Test PII redaction service."""

    def test_redactor_creation(self):
        """Test redaction service can be instantiated."""
        from app.services.document.redactor import RedactorService

        service = RedactorService()
        assert service is not None

    def test_redaction_result_structure(self):
        """Test RedactionResult dataclass."""
        from app.services.document.redactor import RedactionResult

        result = RedactionResult(
            original_text="test email@test.com",
            redacted_text="test [REDACTED]",
            redactions_applied=1,
            pii_types_found={"email": 1},
        )

        assert result.original_text == "test email@test.com"
        assert result.redacted_text == "test [REDACTED]"
        assert result.redactions_applied == 1

    def test_email_redaction(self):
        """Test email redaction."""
        from app.services.document.redactor import RedactorService

        service = RedactorService()
        text = "Contact us at support@example.com"
        
        result = service.redact(text, ["email"])
        
        assert "[REDACTED]" in result.redacted_text
        assert "email" in result.pii_types_found

    def test_ssn_redaction(self):
        """Test SSN redaction."""
        from app.services.document.redactor import RedactorService

        service = RedactorService()
        text = "SSN: 123-45-6789"
        
        result = service.redact(text, ["ssn"])
        
        assert "[REDACTED]" in result.redacted_text


class TestDocumentComparator:
    """Test document comparison service."""

    def test_comparator_creation(self):
        """Test comparator can be instantiated."""
        from app.services.document.comparator import DocumentComparator

        comp = DocumentComparator()
        assert comp is not None

    def test_comparison_result_structure(self):
        """Test ComparisonResult dataclass."""
        from app.services.document.comparator import ComparisonResult

        result = ComparisonResult(
            document1={"id": "doc1", "filename": "f1.txt"},
            document2={"id": "doc2", "filename": "f2.txt"},
            overall_similarity=0.85,
            similar_sections=[],
            key_differences=[],
            processing_time_ms=100,
        )

        assert result.overall_similarity == 0.85


class TestBatchProcessor:
    """Test batch processing service."""

    def test_batch_creation(self):
        """Test batch processor can be instantiated."""
        from app.services.document.batch import BatchProcessor

        processor = BatchProcessor()
        assert processor is not None

    def test_batch_job_status_structure(self):
        """Test BatchJobStatus dataclass."""
        from app.services.document.batch import BatchJobStatus

        status = BatchJobStatus(
            batch_id="batch_001",
            status="pending",
            total_files=10,
            processed_files=0,
            failed_files=0,
        )

        assert status.batch_id == "batch_001"
        assert status.total_files == 10
        assert status.status == "pending"

    def test_max_files_validation(self):
        """Test max files limit."""
        from app.services.document.batch import BatchProcessor

        processor = BatchProcessor()
        
        # This should be within limits
        batch = processor.create_batch(5)
        assert batch.total_files == 5


class TestExportServices:
    """Test export services."""

    def test_pdf_exporter(self):
        """Test PDF exporter."""
        from app.services.export.pdf import PDFExporter

        exporter = PDFExporter()
        assert exporter is not None

    def test_csv_exporter(self):
        """Test CSV exporter."""
        from app.services.export.csv import CSVExporter

        exporter = CSVExporter()
        assert exporter is not None

    def test_csv_entities_export(self):
        """Test CSV entity export."""
        from app.services.export.csv import CSVExporter

        exporter = CSVExporter()
        entities = {
            "persons": ["John", "Jane"],
            "emails": ["john@test.com"],
        }

        result = exporter.export_entities(entities)
        
        assert b"persons" in result
        assert b"John" in result

    def test_markdown_exporter(self):
        """Test Markdown exporter."""
        from app.services.export.markdown import MarkdownExporter

        exporter = MarkdownExporter()
        assert exporter is not None

    def test_markdown_export(self):
        """Test Markdown export format."""
        from app.services.export.markdown import MarkdownExporter

        exporter = MarkdownExporter()
        
        analysis = {
            "classification": {"type": "invoice", "confidence": 0.95},
            "summary": "Test summary",
            "entities": {"persons": ["John"]},
            "key_insights": ["Insight 1"],
        }
        metadata = {"filename": "test.pdf"}
        
        result = exporter.export(analysis, metadata)
        
        assert "# Document Analysis Report" in result
        assert "invoice" in result


class TestAutoAnalysisService:
    """Test auto-analysis service."""

    def test_service_creation(self):
        """Test auto-analysis can be instantiated."""
        from app.services.analysis.auto_analysis import AutoAnalysisService

        service = AutoAnalysisService()
        assert service is not None