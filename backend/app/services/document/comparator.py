"""
Document Comparison Service - DocuLens AI v4.0
Semantic diff between documents
"""

from dataclasses import dataclass
from typing import Optional

from app.services.llm.llm_service import LLMService


@dataclass
class ComparisonResult:
    document1: dict
    document2: dict
    overall_similarity: float
    similar_sections: list
    key_differences: list
    processing_time_ms: int


class DocumentComparator:
    """Compare documents semantically."""

    def __init__(self):
        self.llm = LLMService()

    def compare(
        self,
        text1: str,
        text2: str,
        doc1_metadata: Optional[dict] = None,
        doc2_metadata: Optional[dict] = None,
        focus: Optional[str] = None,
    ) -> ComparisonResult:
        """Compare two documents."""
        import time
        start_time = time.time()

        metadata1 = doc1_metadata or {}
        metadata2 = doc2_metadata or {}

        prompt = f"""Compare these two documents and provide a detailed analysis.

{f'Focus area: {focus}' if focus else ''}

Document 1:
{text1[:2000]}

Document 2:
{text2[:2000]}

Provide analysis in this format:
similarity: <0.0-1.0>
sections:
- s1: <similar section from doc1>
  s2: <similar section from doc2>  
  similarity: <0.0-1.0>
differences:
- <key difference>
"""

        response = self.llm.generate(prompt)

        similar_sections = []
        key_differences = []
        similarity_score = 0.5

        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("similarity:"):
                try:
                    similarity_score = float(line.split(":")[1].strip())
                except ValueError:
                    pass
            elif line.startswith("-"):
                key_differences.append(line[1:].strip())

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ComparisonResult(
            document1={
                "id": metadata1.get("document_id", "doc_1"),
                "filename": metadata1.get("filename", "Document 1"),
                "content_length": len(text1),
            },
            document2={
                "id": metadata2.get("document_id", "doc_2"),
                "filename": metadata2.get("filename", "Document 2"),
                "content_length": len(text2),
            },
            overall_similarity=similarity_score,
            similar_sections=similar_sections,
            key_differences=key_differences,
            processing_time_ms=processing_time_ms,
        )


document_comparator = DocumentComparator()