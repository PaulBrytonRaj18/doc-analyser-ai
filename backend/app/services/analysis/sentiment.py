"""
Sentiment Analysis Service - DocuLens AI v4.0
"""

from dataclasses import dataclass
from app.services.llm.llm_service import LLMService


@dataclass
class SentimentResult:
    label: str
    score: float


class SentimentService:
    """Analyzes sentiment and tone of documents."""

    def __init__(self):
        self.llm = LLMService()

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of document text."""
        prompt = f"""Analyze the sentiment of the following document.
Return ONLY the sentiment label and score in this format:
label: <positive|neutral|negative>
score: <float between -1.0 and 1.0>

Document text:
{text[:2000]}"""

        response = self.llm.generate(prompt)

        try:
            label = "neutral"
            score = 0.0

            for line in response.strip().split("\n"):
                if line.startswith("label:"):
                    label = line.split(":", 1)[1].strip().lower()
                elif line.startswith("score:"):
                    try:
                        score = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass

            return SentimentResult(label=label, score=score)

        except Exception:
            return SentimentResult(label="neutral", score=0.0)