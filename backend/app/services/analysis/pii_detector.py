"""
PII Detection Service - DocuLens AI v4.0
"""

from dataclasses import dataclass, field
from typing import Optional
from app.services.llm.llm_service import LLMService
from app.core.config import settings


@dataclass
class PIIResult:
    pii_detected: bool
    pii_types: list[str] = field(default_factory=list)
    locations: list[dict] = field(default_factory=list)


class PIIDetector:
    """Detects PII in documents."""

    def __init__(self):
        self.llm = LLMService()
        self.enabled = settings.pii_detection_enabled

    def detect(self, text: str) -> PIIResult:
        """Detect PII in document text."""
        if not self.enabled:
            return PIIResult(pii_detected=False, pii_types=[])

        prompt = f"""Detect Personally Identifiable Information (PII) in the following document.
Return ONLY the detected PII types in this format:
pii_types: <comma-separated types>
locations: <json array of {{"type": "..."| "start": 0, "end": 0}}>

PII types to detect:
- person_name
- email_address
- phone_number
- ssn
- credit_card
- date_of_birth
- address

Document text:
{text[:3000]}"""

        response = self.llm.generate(prompt)

        try:
            pii_types = []
            locations = []

            for line in response.strip().split("\n"):
                if line.startswith("pii_types:"):
                    pii = line.split(":", 1)[1].strip()
                    pii_types = [p.strip() for p in pii.split(",") if p.strip()]
                elif line.startswith("locations:"):
                    import json

                    try:
                        locations = json.loads(line.split(":", 1)[1].strip())
                    except Exception:
                        pass

            return PIIResult(
                pii_detected=len(pii_types) > 0,
                pii_types=pii_types,
                locations=locations,
            )

        except Exception:
            return PIIResult(pii_detected=False, pii_types=[])