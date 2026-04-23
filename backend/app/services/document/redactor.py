"""
PII Redaction Service - DocuLens AI v4.0
PII anonymization and masking
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Dict

from app.core.config import settings


PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[ -]?){3}\d{4}\b',
    "date_of_birth": r'\b(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])/\d{2,4}\b',
    "address": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Plaza|Way)\b',
    "person_name": None,  # Uses NER
}


@dataclass
class RedactionResult:
    original_text: str
    redacted_text: str
    redactions_applied: int
    pii_types_found: Dict[str, int]


class RedactorService:
    """PII redaction and anonymization."""

    def __init__(self):
        self.enabled = settings.pii_detection_enabled
        self.replacement = "[REDACTED]"

    def redact(
        self,
        text: str,
        pii_types: Optional[List[str]] = None,
        replacement: Optional[str] = None,
        use_ner: bool = True,
    ) -> RedactionResult:
        """Redact PII from text."""
        if not self.enabled:
            return RedactionResult(
                original_text=text,
                redacted_text=text,
                redactions_applied=0,
                pii_types_found={},
            )

        pii_types = pii_types or list(PII_PATTERNS.keys())
        replacement = replacement or self.replacement
        
        redacted = text
        pii_counts = {}

        for pii_type in pii_types:
            if pii_type == "person_name":
                if use_ner:
                    redacted, count = self._redact_person_names(redacted, replacement)
                    if count > 0:
                        pii_counts[pii_type] = count
            else:
                pattern = PII_PATTERNS.get(pii_type)
                if pattern:
                    redacted, count = self._redact_pattern(
                        redacted, pii_type, pattern, replacement
                    )
                    pii_counts[pii_type] = count

        redactions_applied = sum(pii_counts.values())

        return RedactionResult(
            original_text=text,
            redacted_text=redacted,
            redactions_applied=redactions_applied,
            pii_types_found=pii_counts,
        )

    def _redact_pattern(
        self,
        text: str,
        pii_type: str,
        pattern: str,
        replacement: str,
    ) -> tuple[str, int]:
        """Redact pattern matches."""
        regex = re.compile(pattern, re.IGNORECASE)
        matches = list(regex.finditer(text))
        count = len(matches)
        
        redacted = regex.sub(replacement, text)
        
        return redacted, count

    def _redact_person_names(
        self,
        text: str,
        replacement: str,
    ) -> tuple[str, int]:
        """Redact person names using NER."""
        from app.services.analysis.ner import NERService
        
        ner = NERService()
        entities = ner.extract_entities(text)
        
        redacted = text
        count = 0
        
        for name in entities.persons:
            if name and len(name) > 1:
                pattern = re.compile(re.escape(name), re.IGNORECASE)
                if pattern.search(redacted):
                    redacted = pattern.sub(replacement, redacted)
                    count += 1

        return redacted, count

    def redact_document(
        self,
        text: str,
        pii_types: Optional[List[str]] = None,
    ) -> RedactionResult:
        """Full document redaction."""
        return self.redact(text, pii_types)


redactor_service = RedactorService()