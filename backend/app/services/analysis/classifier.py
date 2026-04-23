"""
Document Classification Service - DocuLens AI v4.0
12-category document classifier
"""

from dataclasses import dataclass
from typing import Optional

from app.core.config import settings
from app.services.llm.llm_service import LLMService


DOCUMENT_TYPES = [
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


@dataclass
class ClassificationResult:
    document_type: str
    sub_type: Optional[str]
    confidence: float


class ClassificationService:
    """Classifies documents into 12 categories."""

    def __init__(self):
        self.llm = LLMService()

    def classify(self, text: str) -> ClassificationResult:
        """Classify document type using LLM."""
        prompt = f"""Classify the following document into ONE of these categories:
{', '.join(DOCUMENT_TYPES)}

Respond with ONLY the category name and a confidence score (0.0-1.0) in this format:
category: <type>
confidence: <score>
sub_type: <optional subtype>

Document text:
{text[:2000]}"""

        response = self.llm.generate(prompt)

        try:
            lines = response.strip().split("\n")
            doc_type = "general"
            confidence = 0.5
            sub_type = None

            for line in lines:
                if line.startswith("category:"):
                    doc_type = line.split(":", 1)[1].strip().lower()
                elif line.startswith("confidence:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif line.startswith("sub_type:"):
                    sub_type = line.split(":", 1)[1].strip() or None

            if doc_type not in DOCUMENT_TYPES:
                doc_type = "general"

            return ClassificationResult(
                document_type=doc_type,
                sub_type=sub_type,
                confidence=confidence,
            )

        except Exception:
            return ClassificationResult(
                document_type="general",
                sub_type=None,
                confidence=0.5,
            )