"""
Test suite for AI-Powered Document Analysis & Extraction API
Run with: pytest tests/ -v
"""

import io
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Set dummy env vars before importing app
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

from main import app

client = TestClient(app)

# Module where functions are actually imported (patch at usage site)
R = "routers.analyze"

MOCK_AI_RESULT = {
    "document_type": "Report",
    "summary": {
        "bullets": [
            "The document covers software development best practices.",
            "Key stakeholders include John Doe and Acme Corp.",
            "Financial projections show $50,000 in planned spending.",
        ],
        "tldr": "A report on software development practices and projections.",
    },
    "entities": {
        "people": ["John Doe", "Jane Smith"],
        "organizations": ["Acme Corp", "TechStart Inc"],
        "dates": ["January 2024", "Q3 2023"],
        "amounts": ["$50,000", "$1.2M"],
    },
    "sentiment": {
        "label": "positive",
        "confidence": 82,
        "reason": "The document discusses positive outcomes and achievements.",
    },
}


# ─── Health ────────────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_serves_html(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_health(self):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


# ─── PDF Analysis ─────────────────────────────────────────────────────────────

class TestPDFAnalysis:
    @patch(f"{R}.analyze_with_ai", return_value=MOCK_AI_RESULT)
    @patch(f"{R}.extract_text_from_pdf")
    @patch(f"{R}.detect_file_type", return_value=("pdf", "application/pdf"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    def test_pdf_analysis_success(self, mock_validate, mock_detect, mock_extract, mock_ai):
        mock_extract.return_value = ("This is extracted PDF content with many words.", 3)
        pdf = io.BytesIO(b"fake pdf bytes")
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("document.pdf", pdf, "application/pdf")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["file_type"] == "pdf"
        assert data["filename"] == "document.pdf"
        assert data["document_type"] == "Report"
        assert "bullets" in data["summary"]
        assert "tldr" in data["summary"]
        assert "entities" in data
        assert "sentiment" in data
        assert "processing_steps" in data
        assert data["word_count"] > 0

    @patch(f"{R}.analyze_with_ai", return_value=MOCK_AI_RESULT)
    @patch(f"{R}.extract_text_from_pdf")
    @patch(f"{R}.detect_file_type", return_value=("pdf", "application/pdf"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    def test_pdf_response_structure(self, mock_validate, mock_detect, mock_extract, mock_ai):
        mock_extract.return_value = ("Sample text extracted from document.", 2)
        pdf = io.BytesIO(b"fake pdf bytes")
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("report.pdf", pdf, "application/pdf")},
        )
        data = resp.json()

        # Check entity structure
        entities = data["entities"]
        assert "people" in entities
        assert "organizations" in entities
        assert "dates" in entities
        assert "amounts" in entities

        # Check sentiment structure
        sentiment = data["sentiment"]
        assert "label" in sentiment
        assert sentiment["label"] in ("positive", "negative", "neutral")
        assert "confidence" in sentiment
        assert 0 <= sentiment["confidence"] <= 100
        assert "reason" in sentiment

        # Check processing time & steps
        assert data["processing_time_ms"] > 0
        assert "uploaded" in data["processing_steps"]


# ─── DOCX Analysis ───────────────────────────────────────────────────────────

class TestDOCXAnalysis:
    @patch(f"{R}.analyze_with_ai", return_value=MOCK_AI_RESULT)
    @patch(f"{R}.extract_text_from_docx")
    @patch(f"{R}.detect_file_type", return_value=("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    def test_docx_analysis_success(self, mock_validate, mock_detect, mock_extract, mock_ai):
        mock_extract.return_value = ("Word document with detailed content and analysis.", 10)
        docx = io.BytesIO(b"fake docx bytes")
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("report.docx", docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["file_type"] == "docx"
        assert data["status"] == "success"
        assert data["document_type"] == "Report"


# ─── Image Analysis ──────────────────────────────────────────────────────────

class TestImageAnalysis:
    @patch(f"{R}.analyze_with_ai", return_value=MOCK_AI_RESULT)
    @patch(f"{R}.extract_text_from_image")
    @patch(f"{R}.detect_file_type", return_value=("image", "image/png"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    def test_image_analysis_success(self, mock_validate, mock_detect, mock_extract, mock_ai):
        mock_extract.return_value = ("Text extracted from image via OCR.", "tesseract")
        img = io.BytesIO(b"fake image bytes")
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("scan.png", img, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["file_type"] == "image"
        assert "ocr_complete" in data["processing_steps"]


# ─── Error Handling ───────────────────────────────────────────────────────────

class TestErrorHandling:
    @patch(f"{R}.validate_file", return_value=(False, "File is empty"))
    def test_empty_file_rejected(self, mock_validate):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
        )
        assert resp.status_code == 400

    @patch(f"{R}.validate_file", return_value=(False, "Unsupported file type"))
    def test_unsupported_file_type_rejected(self, mock_validate):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("data.csv", io.BytesIO(b"a,b,c"), "text/csv")},
        )
        assert resp.status_code == 400

    @patch(f"{R}.detect_file_type", return_value=("pdf", "application/pdf"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    @patch(f"{R}.extract_text_from_pdf", return_value=("", 0))
    def test_empty_extracted_text_returns_422(self, mock_extract, mock_validate, mock_detect):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("blank.pdf", io.BytesIO(b"fake"), "application/pdf")},
        )
        assert resp.status_code == 422

    def test_missing_file_field_returns_422(self):
        resp = client.post("/api/v1/analyze")
        assert resp.status_code == 422


# ─── Sentiment Values ─────────────────────────────────────────────────────────

class TestSentimentValidation:
    @pytest.mark.parametrize("label", ["positive", "negative", "neutral"])
    @patch(f"{R}.analyze_with_ai")
    @patch(f"{R}.extract_text_from_pdf")
    @patch(f"{R}.detect_file_type", return_value=("pdf", "application/pdf"))
    @patch(f"{R}.validate_file", return_value=(True, ""))
    def test_sentiment_labels(self, mock_validate, mock_detect, mock_extract, mock_ai, label):
        mock_extract.return_value = ("Some document content.", 3)
        mock_ai.return_value = {
            **MOCK_AI_RESULT,
            "sentiment": {"label": label, "confidence": 75, "reason": "Test reason."},
        }
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("doc.pdf", io.BytesIO(b"fake"), "application/pdf")},
        )
        assert resp.status_code == 200
        assert resp.json()["sentiment"]["label"] == label
