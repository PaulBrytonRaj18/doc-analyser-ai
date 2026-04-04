"""
AI Processing Service for Summarization, NER, and Sentiment Analysis.
"""

import json
import re
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger
from app.services.llm.llm_service import llm_service

logger = get_logger(__name__)


class AIProcessingError(Exception):
    """Custom exception for AI processing errors."""

    pass


class AIProcessingService:
    """Service for AI-powered document analysis."""

    def analyze_document(self, text: str, max_length: int = 15000) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis on document text.

        Returns: {
            "summary": str,
            "entities": {
                "persons": [],
                "organizations": [],
                "dates": [],
                "locations": [],
                "monetary_values": []
            },
            "sentiment": "positive|negative|neutral"
        }
        """
        truncated_text = text[:max_length] if len(text) > max_length else text

        llm_available = self._check_llm_available()

        if llm_available:
            summary = self._generate_summary(truncated_text)
            entities = self._extract_entities(truncated_text)
            sentiment = self._analyze_sentiment(truncated_text)
        else:
            logger.warning("LLM not available, using fallback extraction")
            summary = self._generate_summary_fallback(truncated_text)
            entities = self._extract_entities_fallback(truncated_text)
            sentiment = self._analyze_sentiment_fallback(truncated_text)

        return {
            "summary": summary,
            "entities": entities,
            "sentiment": sentiment,
        }

    def _check_llm_available(self) -> bool:
        """Check if LLM service is available."""
        try:
            from app.services.llm.llm_service import llm_service

            client, model = llm_service._get_client()
            return model is not None
        except Exception:
            return False

    def _generate_summary(self, text: str) -> str:
        """Generate concise document summary using LLM."""
        prompt = f"""Generate a concise summary (MAXIMUM 150 WORDS) of the following document.
Focus on the main topics, key points, and overall purpose. Be accurate and do not hallucinate.

Document:
{text}

Summary:"""

        try:
            response = llm_service.generate_sync(
                prompt=prompt,
                system_instruction="You are an expert at summarizing documents concisely and accurately.",
                max_tokens=500,
                temperature=0.3,
            )

            summary = response.content.strip()

            words = summary.split()
            if len(words) > 150:
                summary = " ".join(words[:150])
                if summary[-1] not in ".!?":
                    summary += "..."

            return summary if summary else "Summary not available"

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary generation failed"

    def _extract_entities(self, text: str) -> Dict[str, list]:
        """Extract named entities using LLM."""
        prompt = f"""Extract named entities from the document below.
Return ONLY a valid JSON object with these keys: persons, organizations, dates, locations, monetary_values
Do not include any other text or explanation.

Document:
{text}

JSON:"""

        try:
            response = llm_service.generate_sync(
                prompt=prompt,
                system_instruction="You are an expert at entity extraction. Return ONLY valid JSON.",
                max_tokens=1500,
                temperature=0.2,
            )

            entities = self._parse_entity_response(response.content)
            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                "persons": [],
                "organizations": [],
                "dates": [],
                "locations": [],
                "monetary_values": [],
            }

    def _parse_entity_response(self, response: str) -> Dict[str, list]:
        """Parse entity extraction response, handling various formats."""
        cleaned = response.strip()

        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]

        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return {
                "persons": list(set(data.get("persons", []))),
                "organizations": list(set(data.get("organizations", []))),
                "dates": list(set(data.get("dates", []))),
                "locations": list(set(data.get("locations", []))),
                "monetary_values": list(set(data.get("monetary_values", []))),
            }
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{[\s\S]*\}", cleaned)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return {
                    "persons": list(set(data.get("persons", []))),
                    "organizations": list(set(data.get("organizations", []))),
                    "dates": list(set(data.get("dates", []))),
                    "locations": list(set(data.get("locations", []))),
                    "monetary_values": list(set(data.get("monetary_values", []))),
                }
            except Exception:
                pass

        return {
            "persons": [],
            "organizations": [],
            "dates": [],
            "locations": [],
            "monetary_values": [],
        }

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze document sentiment using LLM."""
        prompt = f"""Analyze the sentiment of the document below.
Return ONLY one word: "positive", "negative", or "neutral"
Do not include any other text.

Document:
{text}

Sentiment:"""

        try:
            response = llm_service.generate_sync(
                prompt=prompt,
                system_instruction="Classify sentiment as positive, negative, or neutral.",
                max_tokens=50,
                temperature=0.2,
            )

            sentiment = response.content.strip().lower()

            if "positive" in sentiment:
                return "positive"
            elif "negative" in sentiment:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return "neutral"

    def _generate_summary_fallback(self, text: str) -> str:
        """Generate summary using basic text extraction."""
        sentences = text.split(".")
        if sentences:
            return sentences[0].strip() + "."
        return text[:150] + "..."

    def _extract_entities_fallback(self, text: str) -> Dict[str, list]:
        """Extract entities using regex patterns."""
        import re

        persons = []
        orgs = []
        dates = []
        locations = []
        money = []

        capital_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
        persons = list(set(re.findall(capital_pattern, text)))[:10]

        org_pattern = (
            r"\b[A-Z][A-Z]+(?:\s+(?:Corp|Inc|LLC|Ltd|Co|Company|Organization))\b"
        )
        orgs = list(set(re.findall(org_pattern, text)))[:10]

        date_patterns = [
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        ]
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        dates = list(set(dates))[:10]

        loc_pattern = r"\b(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Washington|Boston|Atlanta|Miami|Seattle)\b"
        locations = list(set(re.findall(loc_pattern, text, re.IGNORECASE)))[:10]

        money_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"
        money = list(set(re.findall(money_pattern, text)))[:10]

        return {
            "persons": persons,
            "organizations": orgs,
            "dates": dates,
            "locations": locations,
            "monetary_values": money,
        }

    def _analyze_sentiment_fallback(self, text: str) -> str:
        """Simple sentiment analysis using keyword matching."""
        text_lower = text.lower()

        positive_words = [
            "good",
            "great",
            "excellent",
            "positive",
            "success",
            "growth",
            "improve",
            "benefit",
            "profit",
            "happy",
        ]
        negative_words = [
            "bad",
            "poor",
            "negative",
            "fail",
            "loss",
            "decline",
            "problem",
            "issue",
            "risk",
            "concern",
        ]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"


ai_processing_service = AIProcessingService()
