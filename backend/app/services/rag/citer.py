"""
Citation Builder Service - DocuLens AI v4.0
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Citation:
    document_id: str
    chunk_id: str
    page: Optional[int]
    region: Optional[dict]
    excerpt: str
    relevance_score: float


class CitationService:
    """Builds source citations for RAG responses."""

    def build_citations(
        self,
        sources: list[dict],
        retrieved_chunks: list[dict],
    ) -> list[Citation]:
        """Build citations from retrieved sources."""
        citations = []

        for source_data in sources:
            doc_id = source_data.get("document_id", "unknown")
            chunk_id = source_data.get("chunk_id", f"{doc_id}_chunk_0")
            page = source_data.get("page")
            region = source_data.get("region")
            relevance = source_data.get("relevance_score", 0.0)

            excerpt = ""
            for chunk in retrieved_chunks:
                if chunk.get("id") == chunk_id:
                    excerpt = chunk.get("text", "")[:200]
                    break

            citations.append(
                Citation(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    page=page,
                    region=region,
                    excerpt=excerpt,
                    relevance_score=relevance,
                )
            )

        return citations

    def format_citation(self, citation: Citation) -> str:
        """Format a single citation for display."""
        source = f"Document: {citation.document_id}"
        if citation.page:
            source += f", Page: {citation.page}"
        source += f" (Relevance: {citation.relevance_score:.2f})"
        return source