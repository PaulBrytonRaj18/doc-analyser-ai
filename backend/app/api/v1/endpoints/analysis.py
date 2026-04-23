"""
Advanced Analysis API Endpoints (Synthesis, Comparison, Insights).
"""

import json
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    SynthesisRequest,
    SynthesisResponse,
    ComparisonRequest,
    ComparisonResponse,
    InsightExtractionRequest,
    InsightExtractionResponse,
)
from app.services.vector.vector_store import vector_store_service
from app.services.embedding.embedding_service import embedding_service
from app.services.llm.llm_service import llm_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analysis", tags=["Advanced Analysis"])


@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_documents(request: SynthesisRequest):
    """Synthesize information from multiple documents."""
    try:
        query_vector = embedding_service.generate_embedding(request.query)

        if not query_vector:
            raise HTTPException(
                status_code=500, detail="Failed to generate query embedding"
            )

        results = vector_store_service.search_similar(
            query_vector=query_vector, top_k=request.max_documents * 5
        )

        if not results:
            return SynthesisResponse(
                query=request.query,
                title="No Documents Found",
                executive_summary="No relevant documents found.",
                sections=[],
                source_documents=[],
                key_findings=[],
                confidence_score=0.0,
                processing_time_ms=0,
            )

        doc_contents: dict = {}
        for result in results:
            doc_id = result.metadata.get("document_id", "unknown")
            if doc_id not in doc_contents:
                doc_contents[doc_id] = {
                    "filename": result.metadata.get("filename", "Unknown"),
                    "content": [],
                    "score": 0,
                }
            doc_contents[doc_id]["content"].append(result.content)
            doc_contents[doc_id]["score"] += result.score

        context = _build_synthesis_context(request.query, doc_contents)

        system_prompt = """You are DocuLens AI, an expert at synthesizing information from multiple documents.
Create a comprehensive synthesis with:
1. Clear title
2. Executive summary (2-3 sentences)
3. Logical sections with findings
4. Identify patterns and conflicts

Be factual and cite sources."""

        prompt = (
            f"<query>{request.query}</query>\n\n<documents>\n{context}\n</documents>"
        )

        response = await llm_service.generate(prompt, system_prompt, max_tokens=3000)

        sections = _parse_synthesis_sections(response.content)

        source_docs = [
            {
                "document_id": doc_id,
                "filename": data["filename"],
                "score": data["score"] / len(data["content"]),
            }
            for doc_id, data in list(doc_contents.items())[: request.max_documents]
        ]

        return SynthesisResponse(
            query=request.query,
            title=_extract_title(response.content) or f"Synthesis: {request.query}",
            executive_summary=_extract_summary(response.content),
            sections=sections,
            source_documents=source_docs,
            key_findings=_extract_key_findings(sections),
            contradictions=_detect_contradictions(doc_contents),
            confidence_score=_calculate_confidence(results),
            processing_time_ms=0,
            metadata={"documents_analyzed": len(doc_contents)},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_documents(request: ComparisonRequest):
    """Compare two documents."""
    try:
        doc1_results = _get_document_content(request.document1_id)
        doc2_results = _get_document_content(request.document2_id)

        if not doc1_results or not doc2_results:
            raise HTTPException(
                status_code=404, detail="One or both documents not found"
            )

        doc1_content = " ".join(r.content for r in doc1_results)
        doc2_content = " ".join(r.content for r in doc2_results)

        doc1_vector = embedding_service.generate_embedding(doc1_content[:5000])
        doc2_vector = embedding_service.generate_embedding(doc2_content[:5000])

        semantic_similarity = 0.0
        if doc1_vector and doc2_vector:
            semantic_similarity = embedding_service.compute_similarity(
                doc1_vector, doc2_vector
            )

        words1 = set(doc1_content.lower().split())
        words2 = set(doc2_content.lower().split())
        content_overlap = (
            len(words1 & words2) / len(words1 | words2) if words1 and words2 else 0
        )

        system_prompt = """Compare two documents and identify:
1. Common topics (5-7 topics)
2. Key differences
3. Conflicts or contradictions

Respond in JSON format."""

        prompt = (
            f"Document 1:\n{doc1_content[:2500]}\n\nDocument 2:\n{doc2_content[:2500]}"
        )

        response = await llm_service.generate(prompt, system_prompt, max_tokens=1500)

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            analysis = {"common_topics": [], "differences": [], "conflicts": []}

        return ComparisonResponse(
            document1={
                "id": request.document1_id,
                "filename": doc1_results[0].metadata.get("filename", "Unknown"),
                "content_length": len(doc1_content),
            },
            document2={
                "id": request.document2_id,
                "filename": doc2_results[0].metadata.get("filename", "Unknown"),
                "content_length": len(doc2_content),
            },
            overall_similarity=round(
                (semantic_similarity * 0.7 + content_overlap * 0.3), 4
            ),
            content_overlap=round(content_overlap, 4),
            semantic_similarity=round(semantic_similarity, 4),
            common_topics=analysis.get("common_topics", []),
            key_differences=analysis.get("differences", []),
            conflict_areas=analysis.get("conflicts", []),
            recommendations=_generate_comparison_recommendations(
                semantic_similarity, analysis
            ),
            processing_time_ms=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights", response_model=InsightExtractionResponse)
async def extract_insights(request: InsightExtractionRequest):
    """Extract structured insights from documents."""
    try:
        if request.document_id:
            results = _get_document_content(request.document_id)
            if results:
                text = " ".join(r.content for r in results)
                filename = results[0].metadata.get("filename", "Document")
            else:
                raise HTTPException(status_code=404, detail="Document not found")
        else:
            text = request.text
            filename = request.filename or "Document"

        system_prompt = """Extract structured insights from documents. Return JSON with:
- action_items: Tasks with title, description, assigned_to, due_date, priority
- decisions: Decisions with title, description
- deadlines: Important dates with title, date, description
- risks: Potential risks with title, description, severity
- opportunities: Opportunities with title, description
- key_metrics: Important numbers with title, value, description

Focus on: action_item, decision, deadline, risk, key_metric"""

        prompt = f"Extract insights from:\n\n{text[:10000]}"

        response = await llm_service.generate(prompt, system_prompt, max_tokens=2500)

        try:
            insights = json.loads(response.content)
        except json.JSONDecodeError:
            insights = {
                "action_items": [],
                "decisions": [],
                "deadlines": [],
                "risks": [],
                "opportunities": [],
                "key_metrics": [],
            }

        return InsightExtractionResponse(
            document_id=request.document_id or "unknown",
            filename=filename,
            action_items=_format_insights(
                insights.get("action_items", []), "action_item"
            ),
            decisions=_format_insights(insights.get("decisions", []), "decision"),
            deadlines=_format_insights(insights.get("deadlines", []), "deadline"),
            risks=_format_insights(insights.get("risks", []), "risk"),
            opportunities=_format_insights(
                insights.get("opportunities", []), "opportunity"
            ),
            key_metrics=_format_insights(insights.get("key_metrics", []), "key_metric"),
            summary=_generate_insight_summary(insights),
            confidence_score=_calculate_insight_confidence(insights),
            processing_time_ms=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insight extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_document_content(document_id: str):
    """Get full document content from vector store."""
    return vector_store_service.search_similar(
        query_vector=[0.0] * 768,
        top_k=100,
        filters={"document_id": {"$eq": document_id}},
    )


def _build_synthesis_context(query: str, doc_contents: dict) -> str:
    """Build context for synthesis."""
    context = f"Query: {query}\n\n"
    for i, (doc_id, data) in enumerate(list(doc_contents.items())[:10], 1):
        context += f"--- Document {i}: {data['filename']} ---\n"
        context += " ".join(data["content"][:5]) + "\n\n"
    return context


def _parse_synthesis_sections(text: str) -> list:
    """Parse synthesis response into sections."""
    sections = []
    lines = text.split("\n")
    current_section = {"title": "General", "content": ""}

    for line in lines:
        if line.startswith("## "):
            if current_section["content"]:
                sections.append(current_section)
            current_section = {"title": line[3:].strip(), "content": ""}
        elif line.startswith("- ") or line.startswith("* "):
            current_section["content"] += line + "\n"

    if current_section["content"]:
        sections.append(current_section)

    return [
        {"title": s["title"], "content": s["content"].strip(), "confidence": 0.8}
        for s in sections
    ]


def _extract_title(text: str) -> Optional[str]:
    """Extract title from synthesis."""
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _extract_summary(text: str) -> str:
    """Extract executive summary."""
    lines = text.split("\n")
    summary_lines = []
    capture = False
    for line in lines:
        if "summary" in line.lower():
            capture = True
            continue
        if capture and line.strip() and not line.startswith("#"):
            summary_lines.append(line.strip())
            if len(summary_lines) >= 2:
                break
    return " ".join(summary_lines) if summary_lines else text[:300] + "..."


def _extract_key_findings(sections: list) -> list:
    """Extract key findings from sections."""
    findings = []
    for section in sections:
        if any(
            kw in section["title"].lower() for kw in ["finding", "key", "important"]
        ):
            for line in section["content"].split("\n"):
                if line.strip().startswith("-"):
                    findings.append(line.strip()[1:].strip())
    return findings[:5]


def _detect_contradictions(doc_contents: dict) -> list:
    """Detect contradictions in documents."""
    return []


def _calculate_confidence(results: list) -> float:
    """Calculate confidence score."""
    if not results:
        return 0.0
    avg_score = sum(r.score for r in results[:3]) / min(3, len(results))
    return round(avg_score * 100, 2)


def _format_insights(items: list, insight_type: str) -> list:
    """Format insight items."""
    formatted = []
    for item in items[:10]:
        if isinstance(item, dict):
            formatted.append(
                {
                    "type": insight_type,
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "confidence": 0.8,
                    "assigned_to": item.get("assigned_to"),
                    "due_date": item.get("due_date"),
                    "priority": item.get("severity", "medium"),
                }
            )
    return formatted


def _generate_insight_summary(insights: dict) -> str:
    """Generate summary of extracted insights."""
    counts = {k: len(v) for k, v in insights.items() if isinstance(v, list)}
    parts = [
        f"{count} {key.replace('_', ' ')}" for key, count in counts.items() if count > 0
    ]
    return ", ".join(parts) if parts else "Limited insights extracted"


def _calculate_insight_confidence(insights: dict) -> float:
    """Calculate confidence of insight extraction."""
    total = sum(len(v) for v in insights.values() if isinstance(v, list))
    return min(50 + total * 5, 95)


def _generate_comparison_recommendations(similarity: float, analysis: dict) -> list:
    """Generate recommendations based on comparison."""
    recs = []
    if similarity > 0.8:
        recs.append("Documents are highly similar - consider deduplication")
    elif similarity < 0.3:
        recs.append("Documents cover different topics")
    if analysis.get("conflicts"):
        recs.append("Review conflicting claims")
    return recs
