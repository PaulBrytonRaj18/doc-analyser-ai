"""
Confidence Scorer - DocuLens AI v4.0
Per-word and per-region confidence scoring utilities
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class WordConfidence:
    word: str
    confidence: float
    is_low_confidence: bool


@dataclass
class RegionConfidence:
    region_id: int
    average_confidence: float
    low_confidence_words: List[WordConfidence]
    total_words: int


class ConfidenceScorer:
    """Calculate and analyze OCR confidence scores."""

    def __init__(self, low_threshold: float = 0.70, high_threshold: float = 0.90):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def analyze_regions(
        self,
        regions: List[Dict[str, Any]],
    ) -> List[RegionConfidence]:
        """Analyze confidence for each region."""
        results = []

        for region in regions:
            region_id = region.get("region_id", 0)
            words = region.get("words", [])
            
            word_confs = []
            low_conf_words = []

            for word in words:
                conf = word.get("confidence", 0.0)
                word_text = word.get("text", "")
                
                wc = WordConfidence(
                    word=word_text,
                    confidence=conf,
                    is_low_confidence=conf < self.low_threshold,
                )
                word_confs.append(wc)
                
                if conf < self.low_threshold:
                    low_conf_words.append(wc)

            avg_conf = sum(w.confidence for w in word_confs) / len(word_confs) if word_confs else 0.0

            results.append(RegionConfidence(
                region_id=region_id,
                average_confidence=avg_conf,
                low_confidence_words=low_conf_words,
                total_words=len(word_confs),
            ))

        return results

    def get_overall_score(
        self,
        regions: List[Dict[str, Any]],
    ) -> float:
        """Calculate weighted overall confidence."""
        if not regions:
            return 0.0

        total_words = 0
        weighted_sum = 0.0

        for region in regions:
            words = region.get("words", [])
            total_words += len(words)

            region_conf = sum(w.get("confidence", 0.0) for w in words)
            weighted_sum += region_conf

        return weighted_sum / total_words if total_words > 0 else 0.0

    def classify_confidence(
        self,
        confidence: float,
    ) -> str:
        """Classify confidence level."""
        if confidence >= self.high_threshold:
            return "high"
        elif confidence >= self.low_threshold:
            return "medium"
        else:
            return "low"

    def get_color_mapping(self) -> Dict[str, str]:
        """Get color mapping for UI display."""
        return {
            "high": "#10B981",  # Emerald
            "medium": "#F59E0B",  # Amber
            "low": "#F43F5E",  # Rose
        }


# Default instance
confidence_scorer = ConfidenceScorer()