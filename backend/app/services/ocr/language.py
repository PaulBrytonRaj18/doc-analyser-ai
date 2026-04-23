"""
Language Detector - DocuLens AI v4.0
Detect language from text or image
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DetectedLanguage:
    language: str
    confidence: float


LANGUAGE_CODES = {
    "en": "English",
    "tam": "Tamil",
    "hi": "Hindi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "uk": "Ukrainian",
}


class LanguageDetector:
    """Detect language from OCR results or text."""

    # Common words in different languages for pattern matching
    COMMON_WORDS = {
        "en": ["the", "and", "is", "are", "was", "were", "have", "has", "been"],
        "fr": ["le", "la", "les", "et", "est", "sont", "ete", "ete"],
        "de": ["der", "die", "das", "und", "ist", "sind", "war", "waren"],
        "es": ["el", "la", "los", "las", "y", "es", "son", "fue"],
        "it": ["il", "la", "gli", "e", "e", "sono", "era", "erano"],
        "pt": ["o", "a", "os", "as", "e", "sao", "foi", "foram"],
    }

    def detect_from_text(self, text: str) -> List[DetectedLanguage]:
        """Detect language from text content."""
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return [DetectedLanguage("en", 0.5)]

        scores = {}
        
        for lang, common in self.COMMON_WORDS.items():
            count = sum(1 for word in words[:50] if word in common)
            if count > 0:
                scores[lang] = count / min(len(words), 50)

        if not scores:
            return [DetectedLanguage("en", 0.5)]

        max_lang = max(scores, key=scores.get)
        max_score = scores[max_lang]

        return [DetectedLanguage(max_lang, max_score)]

    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        return LANGUAGE_CODES.get(code, code.upper())

    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages."""
        return LANGUAGE_CODES.copy()


# Default instance
language_detector = LanguageDetector()