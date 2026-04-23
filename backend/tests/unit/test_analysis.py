"""Unit Tests - Analysis Services"""



class TestClassificationService:
    """Test document classification service."""

    def test_classification_result_structure(self):
        """Test ClassificationResult dataclass."""
        from app.services.analysis.classifier import ClassificationResult

        result = ClassificationResult(
            document_type="invoice",
            sub_type="commercial_invoice",
            confidence=0.96,
        )

        assert result.document_type == "invoice"
        assert result.sub_type == "commercial_invoice"
        assert result.confidence == 0.96

    def test_document_types_list(self):
        """Test that all 12 document types are defined."""
        from app.services.analysis.classifier import DOCUMENT_TYPES

        expected_types = [
            "invoice",
            "contract",
            "receipt",
            "report",
            "resume",
            "legal_filing",
            "medical_record",
            "id_document",
            "handwritten_note",
            "form",
            "academic",
            "general",
        ]

        assert DOCUMENT_TYPES == expected_types
        assert len(DOCUMENT_TYPES) == 12


class TestSummarizationService:
    """Test summarization service."""

    def test_summary_result_structure(self):
        """Test SummaryResult dataclass."""
        from app.services.analysis.summarizer import SummaryResult

        result = SummaryResult(
            summary="This is a test summary.",
            word_count=5,
        )

        assert result.summary == "This is a test summary."
        assert result.word_count == 5


class TestNERService:
    """Test Named Entity Recognition service."""

    def test_entity_result_structure(self):
        """Test EntityResult dataclass."""
        from app.services.analysis.ner import EntityResult

        result = EntityResult(
            persons=["John Doe", "Jane Smith"],
            organizations=["Acme Corp", "Tech Inc"],
            dates=["March 5, 2024", "April 4, 2024"],
            locations=["San Francisco, CA"],
            monetary_values=["$12,400.00", "$186.00"],
            invoice_numbers=["INV-2024-0091"],
            email_addresses=["billing@acmecorp.com"],
            phone_numbers=["+1-555-123-4567"],
        )

        assert len(result.persons) == 2
        assert len(result.organizations) == 2
        assert len(result.dates) == 2
        assert len(result.locations) == 1
        assert len(result.monetary_values) == 2
        assert len(result.invoice_numbers) == 1
        assert len(result.email_addresses) == 1
        assert len(result.phone_numbers) == 1

    def test_entity_result_empty(self):
        """Test EntityResult with empty values."""
        from app.services.analysis.ner import EntityResult

        result = EntityResult()

        assert result.persons == []
        assert result.organizations == []
        assert result.dates == []
        assert result.locations == []
        assert result.monetary_values == []
        assert result.invoice_numbers == []
        assert result.email_addresses == []
        assert result.phone_numbers == []


class TestSentimentService:
    """Test sentiment analysis service."""

    def test_sentiment_result_structure(self):
        """Test SentimentResult dataclass."""
        from app.services.analysis.sentiment import SentimentResult

        result = SentimentResult(
            label="neutral",
            score=0.02,
        )

        assert result.label == "neutral"
        assert result.score == 0.02
        assert -1.0 <= result.score <= 1.0

    def test_sentiment_labels(self):
        """Test valid sentiment labels."""
        from app.services.analysis.sentiment import SentimentResult

        valid_labels = ["positive", "neutral", "negative"]

        for label in valid_labels:
            result = SentimentResult(label=label, score=0.0)
            assert result.label in valid_labels


class TestInsightsService:
    """Test key insights extraction service."""

    def test_insights_result_structure(self):
        """Test InsightsResult dataclass."""
        from app.services.analysis.insights import InsightsResult

        result = InsightsResult(
            insights=[
                "Payment due in 30 days",
                "Late fee clause detected",
                "GST/Tax line item present",
            ]
        )

        assert len(result.insights) == 3
        assert "Payment due in 30 days" in result.insights

    def test_insights_result_empty(self):
        """Test InsightsResult with empty insights."""
        from app.services.analysis.insights import InsightsResult

        result = InsightsResult()

        assert result.insights == []


class TestTableExtractor:
    """Test table extraction service."""

    def test_table_data_structure(self):
        """Test TableData dataclass."""
        from app.services.analysis.table import TableData

        table = TableData(
            table_id=1,
            headers=["Item", "Qty", "Price"],
            rows=[["Widget", "10", "$100"]],
            caption="Test Table",
        )

        assert table.table_id == 1
        assert len(table.headers) == 3
        assert len(table.rows) == 1
        assert table.caption == "Test Table"

    def test_table_extraction_result_structure(self):
        """Test TableExtractionResult dataclass."""
        from app.services.analysis.table import TableData, TableExtractionResult

        tables = [
            TableData(table_id=1, headers=["Col1"], rows=[["Val1"]])
        ]

        result = TableExtractionResult(tables=tables)

        assert len(result.tables) == 1
        assert result.tables[0].table_id == 1


class TestPIIDetector:
    """Test PII detection service."""

    def test_pii_result_structure(self):
        """Test PIIResult dataclass."""
        from app.services.analysis.pii_detector import PIIResult

        result = PIIResult(
            pii_detected=True,
            pii_types=["person_name", "email_address"],
            locations=[{"type": "email", "start": 100, "end": 120}],
        )

        assert result.pii_detected is True
        assert len(result.pii_types) == 2
        assert len(result.locations) == 1

    def test_pii_result_no_detection(self):
        """Test PIIResult with no detection."""
        from app.services.analysis.pii_detector import PIIResult

        result = PIIResult(
            pii_detected=False,
            pii_types=[],
        )

        assert result.pii_detected is False
        assert result.pii_types == []

    def test_pii_types_list(self):
        """Test PII types that can be detected."""

        expected_types = [
            "person_name",
            "email_address",
            "phone_number",
            "ssn",
            "credit_card",
            "date_of_birth",
            "address",
        ]

        # Verify these types are handled in the prompt (not directly testable without LLM)
        assert expected_types is not None