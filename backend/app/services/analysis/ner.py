"""
Named Entity Recognition Service - DocuLens AI v4.0
"""

from dataclasses import dataclass, field
from app.services.llm.llm_service import LLMService


@dataclass
class EntityResult:
    persons: list[str] = field(default_factory=list)
    organizations: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    monetary_values: list[str] = field(default_factory=list)
    invoice_numbers: list[str] = field(default_factory=list)
    email_addresses: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)


class NERService:
    """Extract named entities from documents."""

    def __init__(self):
        self.llm = LLMService()

    def extract_entities(self, text: str) -> EntityResult:
        """Extract all named entities from text."""
        prompt = f"""Extract named entities from the following document.
Return ONLY the entities in this exact format (one per line):

persons: <comma-separated names>
organizations: <comma-separated orgs>
dates: <comma-separated dates>
locations: <comma-separated locations>
monetary_values: <comma-separated amounts>
invoice_numbers: <comma-separated invoice numbers>
email_addresses: <comma-separated emails>
phone_numbers: <comma-separated phone numbers>

Document text:
{text[:3000]}"""

        response = self.llm.generate(prompt)

        try:
            result = EntityResult()
            for line in response.strip().split("\n"):
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = [v.strip() for v in value.split(",") if v.strip()]

                if key == "persons":
                    result.persons = value
                elif key == "organizations":
                    result.organizations = value
                elif key == "dates":
                    result.dates = value
                elif key == "locations":
                    result.locations = value
                elif key == "monetary_values":
                    result.monetary_values = value
                elif key == "invoice_numbers":
                    result.invoice_numbers = value
                elif key == "email_addresses":
                    result.email_addresses = value
                elif key == "phone_numbers":
                    result.phone_numbers = value

            return result
        except Exception:
            return EntityResult()