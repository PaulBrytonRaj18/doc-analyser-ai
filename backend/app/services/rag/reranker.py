"""
RAG Reranker Service - DocuLens AI v4.0
Cross-encoder reranking
"""

from dataclasses import dataclass
from typing import List
from app.services.llm.llm_service import LLMService


@dataclass
class RerankedResult:
    chunk: str
    score: float
    index: int


class RerankerService:
    """Reranks retrieved chunks using cross-encoder."""

    def __init__(self):
        self.llm = LLMService()

    def rerank(
        self, query: str, chunks: List[str], top_k: int = 6
    ) -> List[RerankedResult]:
        """Rerank chunks based on query relevance."""
        if not chunks:
            return []

        prompt = f"""Rank these text chunks by relevance to the query.
Query: {query}

Chunks (respond with only scores, one per line, 0-1 scale):
"""
        for i, chunk in enumerate(chunks):
            prompt += f"{i}: {chunk[:200]}\n"

        response = self.llm.generate(prompt)

        results = []
        try:
            lines = response.strip().split("\n")
            for line in lines:
                line = line.strip()
                if ":" in line or "-" in line:
                    try:
                        parts = line.replace("-", ":").split(":")
                        idx = int(parts[0].strip())
                        score = float(parts[1].strip())
                        results.append(
                            RerankedResult(
                                chunk=chunks[idx], score=score, index=idx
                            )
                        )
                    except (ValueError, IndexError):
                        pass
        except Exception:
            for i, chunk in enumerate(chunks):
                results.append(
                    RerankedResult(chunk=chunk, score=1.0, index=i)
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]