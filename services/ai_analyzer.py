"""
AI-powered analysis using Claude (Anthropic) API.
Handles: document classification, summarisation, entity extraction, sentiment analysis.
"""

import os
import json
import re
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_TEXT_LENGTH = 12000


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_TEXT_LENGTH:
        return text
    third = MAX_TEXT_LENGTH // 3
    return (
        text[:third]
        + "\n\n[... content truncated for analysis ...]\n\n"
        + text[len(text) // 2 - third // 2 : len(text) // 2 + third // 2]
        + "\n\n[... content truncated ...]\n\n"
        + text[-third:]
    )


def analyze_with_ai(text: str) -> Dict[str, Any]:
    """
    Send document text to Claude and get structured analysis.
    Returns dict with document_type, summary, entities, sentiment.
    """
    truncated = _truncate_text(text)

    prompt = f"""You are an expert document analyst. Analyse the following document text and return a structured JSON response.

DOCUMENT TEXT:
{truncated}

Return ONLY a valid JSON object (no markdown, no explanation) with exactly this structure:
{{
  "document_type": "Invoice | Resume | Legal | Research Paper | Complaint | Report | Letter | Contract | Other",
  "summary": {{
    "bullets": ["bullet point 1 capturing a key finding or fact", "bullet point 2", "bullet point 3"],
    "tldr": "A single concise sentence capturing the document's main purpose."
  }},
  "entities": {{
    "people": ["list of full names of people mentioned"],
    "organizations": ["list of companies, institutions, or organisations mentioned"],
    "dates": ["list of all dates, years, or time references mentioned"],
    "amounts": ["list of all currency values, prices, or financial figures mentioned"]
  }},
  "sentiment": {{
    "label": "positive OR negative OR neutral",
    "confidence": 75,
    "reason": "One sentence explaining why this sentiment label was assigned."
  }}
}}

Guidelines:
- document_type: Classify the document into one of: Invoice, Resume, Legal, Research Paper, Complaint, Report, Letter, Contract, or Other. Pick the closest match.
- summary.bullets: 3-5 concise bullet points capturing the key facts, findings, or important information.
- summary.tldr: A single sentence (max 20 words) that captures the core purpose of the document.
- entities: Only include entities explicitly mentioned in the text. No duplicates. Use original casing.
- sentiment.confidence: Integer from 0 to 100 indicating how confident you are in the sentiment label.
- sentiment.reason: Brief explanation of why you assigned this sentiment.
- Return empty arrays [] if no entities found for a category.
- IMPORTANT: Return ONLY the JSON object. No preamble, no markdown code blocks."""

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        logger.debug(f"AI raw response (first 200): {raw[:200]}")

        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()

        result = json.loads(raw)
        return _validate_and_normalize(result)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from AI: {e}\nRaw: {raw[:500]}")
        return _fallback_analysis(text)
    except ImportError:
        logger.error("anthropic library not installed")
        return _fallback_analysis(text)
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return _fallback_analysis(text)


def _validate_and_normalize(data: Dict) -> Dict:
    """Ensure the response has all required fields with correct types."""
    # Document type
    doc_type = str(data.get("document_type", "Other")).strip()
    valid_types = {"Invoice", "Resume", "Legal", "Research Paper", "Complaint", "Report", "Letter", "Contract", "Other"}
    if doc_type not in valid_types:
        doc_type = "Other"

    # Summary
    summary_data = data.get("summary", {})
    if isinstance(summary_data, str):
        bullets = [summary_data]
        tldr = summary_data[:100]
    else:
        bullets_raw = summary_data.get("bullets", [])
        bullets = [str(b).strip() for b in bullets_raw if str(b).strip()] if isinstance(bullets_raw, list) else []
        tldr = str(summary_data.get("tldr", "")).strip()

    # Entities
    entity_keys = ["people", "organizations", "dates", "amounts"]
    entities = data.get("entities", {})
    normalized_entities = {}
    for key in entity_keys:
        val = entities.get(key, [])
        if isinstance(val, list):
            seen = set()
            unique = []
            for item in val:
                item_lower = str(item).lower()
                if item_lower not in seen and str(item).strip():
                    seen.add(item_lower)
                    unique.append(str(item).strip())
            normalized_entities[key] = unique
        else:
            normalized_entities[key] = []

    # Sentiment
    sentiment = data.get("sentiment", {})
    label = str(sentiment.get("label", "neutral")).lower()
    if label not in ("positive", "negative", "neutral"):
        label = "neutral"

    confidence = sentiment.get("confidence", 50)
    try:
        confidence = int(confidence)
    except (ValueError, TypeError):
        confidence = 50
    confidence = max(0, min(100, confidence))

    reason = str(sentiment.get("reason", sentiment.get("explanation", ""))).strip()

    return {
        "document_type": doc_type,
        "summary": {
            "bullets": bullets if bullets else ["No key points extracted."],
            "tldr": tldr if tldr else "Summary not available.",
        },
        "entities": normalized_entities,
        "sentiment": {
            "label": label,
            "confidence": confidence,
            "reason": reason,
        },
    }


def _fallback_analysis(text: str) -> Dict:
    """Basic rule-based fallback when AI is unavailable."""
    words = text.split()
    word_count = len(words)
    sentences = re.split(r"[.!?]+", text)
    first_sentences = [s.strip() for s in sentences[:3] if s.strip()]

    # Simple heuristic sentiment
    positive_words = {"good", "great", "excellent", "success", "positive", "benefit", "improve", "growth"}
    negative_words = {"bad", "fail", "loss", "risk", "problem", "issue", "concern", "decline", "negative"}
    lower_text = text.lower()
    pos_count = sum(1 for w in positive_words if w in lower_text)
    neg_count = sum(1 for w in negative_words if w in lower_text)

    if pos_count > neg_count:
        label, confidence = "positive", 60
    elif neg_count > pos_count:
        label, confidence = "negative", 60
    else:
        label, confidence = "neutral", 50

    # Basic date extraction
    dates = re.findall(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r"|\b\d{4}\b",
        text,
    )
    dates = list(set(dates[:10]))

    # Basic monetary extraction
    money = re.findall(
        r"[\$£€¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?(?:\s?(?:million|billion|thousand|M|B|K))?"
        r"|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|INR)",
        text,
    )
    money = list(set(money[:10]))

    # Simple doc type heuristic
    doc_type = "Other"
    lt = lower_text[:2000]
    if any(k in lt for k in ["invoice", "bill to", "amount due", "payment"]):
        doc_type = "Invoice"
    elif any(k in lt for k in ["resume", "curriculum vitae", "work experience", "education"]):
        doc_type = "Resume"
    elif any(k in lt for k in ["plaintiff", "defendant", "court", "hereby"]):
        doc_type = "Legal"
    elif any(k in lt for k in ["abstract", "methodology", "references", "conclusion"]):
        doc_type = "Research Paper"
    elif any(k in lt for k in ["complaint", "dissatisfied", "unacceptable"]):
        doc_type = "Complaint"

    return {
        "document_type": doc_type,
        "summary": {
            "bullets": first_sentences[:3] if first_sentences else ["Document content extracted successfully."],
            "tldr": first_sentences[0][:100] if first_sentences else "Document content extracted.",
        },
        "entities": {
            "people": [],
            "organizations": [],
            "dates": dates[:5],
            "amounts": money[:5],
        },
        "sentiment": {
            "label": label,
            "confidence": confidence,
            "reason": "Sentiment determined by keyword analysis (AI unavailable).",
        },
    }
