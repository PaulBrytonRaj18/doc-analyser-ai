"""
Key Insights Extraction Service - DocuLens AI v4.0
"""

from dataclasses import dataclass, field
from app.services.llm.llm_service import LLMService


@dataclass
class InsightsResult:
    insights: list[str] = field(default_factory=list)


class InsightsService:
    """Extracts key insights from documents."""

    def __init__(self):
        self.llm = LLMService()

    def extract(self, text: str) -> InsightsResult:
        """Extract key insights from document text."""
        prompt = f"""Extract 3-10 key insights from the following document.
List each insight as a concise bullet point (no numbering):

Document text:
{text[:4000]}"""

        response = self.llm.generate(prompt)

        insights = [
            line.strip()
            for line in response.strip().split("\n")
            if line.strip() and not line.strip().startswith("insight")
        ]

        return InsightsResult(insights=insights)