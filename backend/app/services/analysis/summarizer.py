"""
Summarization Service - DocuLens AI v4.0
"""

from dataclasses import dataclass
from app.services.llm.llm_service import LLMService


@dataclass
class SummaryResult:
    summary: str
    word_count: int


class SummarizationService:
    """Generates document summaries using Gemini."""

    def __init__(self):
        self.llm = LLMService()

    def summarize(self, text: str, max_length: int = 500) -> SummaryResult:
        """Generate a concise summary of the document."""
        prompt = f"""Create a concise summary of the following document in no more than {max_length} words:

{text[:4000]}"""

        summary = self.llm.generate(prompt)

        return SummaryResult(
            summary=summary.strip(),
            word_count=len(summary.split()),
        )