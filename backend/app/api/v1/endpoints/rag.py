"""
RAG (Retrieval-Augmented Generation) API Endpoints.
"""

import json
from typing import Optional, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    SourceReference,
    Citation,
)
from app.services.vector.vector_store import vector_store_service
from app.services.embedding.embedding_service import embedding_service
from app.services.llm.llm_service import llm_service
from app.services.cache.cache_service import cache_service
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_documents(request: RAGQueryRequest):
    """Query documents using RAG."""
    try:
        query_vector = embedding_service.generate_embedding(request.query)

        if not query_vector:
            raise HTTPException(
                status_code=500, detail="Failed to generate query embedding"
            )

        cache_key = f"query:{hashlib.sha256(request.query.encode()).hexdigest()[:16]}"
        cached = cache_service.get(cache_key)
        if cached:
            logger.info("Returning cached query result")
            return RAGQueryResponse(**cached)

        search_results = vector_store_service.search_similar(
            query_vector=query_vector,
            top_k=request.top_k or settings.top_k_results,
            filters=request.filter_dict,
        )

        if not search_results:
            return RAGQueryResponse(
                answer="No relevant documents found for your query.",
                sources=[],
                citations=[],
                confidence=0.0,
                processing_time_ms=0,
            )

        context = _build_context(search_results, request.max_context_chunks)

        system_prompt = """You are DocuLens AI, an intelligent assistant that helps users understand their documents.
Answer questions based ONLY on the provided context. Cite specific information from documents.
If information isn't in the context, say so clearly."""

        prompt = (
            f"<question>{request.query}</question>\n\n<context>\n{context}\n</context>"
        )

        response = await llm_service.generate(
            prompt=prompt, system_instruction=system_prompt, max_tokens=2000
        )

        sources = []
        seen_docs = set()
        for result in search_results[: settings.top_k_results]:
            doc_id = result.metadata.get("document_id", "unknown")
            if doc_id not in seen_docs:
                sources.append(
                    SourceReference(
                        id=result.result_id,
                        document_id=doc_id,
                        filename=result.metadata.get("filename", "Unknown"),
                        score=result.score,
                        page=result.metadata.get("page"),
                        preview=result.content[:200] + "...",
                    )
                )
                seen_docs.add(doc_id)

        confidence = (
            sum(r.score for r in search_results[:3]) / min(3, len(search_results)) * 100
        )

        result_data = {
            "answer": response.content,
            "sources": [s.model_dump() for s in sources],
            "citations": [],
            "confidence": round(confidence, 2),
            "processing_time_ms": 0,
            "query": request.query,
        }

        cache_service.set(cache_key, result_data, ttl=3600)

        return RAGQueryResponse(**result_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=RAGSearchResponse)
async def search_documents(request: RAGSearchRequest):
    """Semantic search across documents."""
    try:
        query_vector = embedding_service.generate_embedding(request.query)

        if not query_vector:
            raise HTTPException(
                status_code=500, detail="Failed to generate query embedding"
            )

        results = vector_store_service.search_similar(
            query_vector=query_vector,
            top_k=request.top_k or settings.top_k_results,
            filters=request.filter_dict,
        )

        return RAGSearchResponse(
            total=len(results),
            results=[
                {
                    "result_id": r.result_id,
                    "score": r.score,
                    "content": r.content[:500],
                    "document_id": r.metadata.get("document_id"),
                    "filename": r.metadata.get("filename"),
                    "page": r.metadata.get("page"),
                    "chunk_index": r.metadata.get("chunk_index"),
                }
                for r in results
            ],
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get RAG system statistics."""
    try:
        vector_stats = vector_store_service.get_statistics()
        cache_stats = cache_service.get_stats()

        return {
            "total_vectors": vector_stats.get("total_vectors", 0),
            "dimension": vector_stats.get("dimension", 0),
            "cache_keys": cache_stats.get("memory_keys", 0),
            "redis_connected": cache_stats.get("redis_connected", False),
        }
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def query_stream_generator(query: str, top_k: int):
    """Generate streaming response for query."""
    try:
        query_vector = embedding_service.generate_embedding(query)

        if not query_vector:
            yield "data: No results found\n\n"
            return

        results = vector_store_service.search_similar(
            query_vector=query_vector, top_k=top_k
        )

        context = _build_context(results, settings.max_context_chunks)

        system_prompt = (
            """You are DocuLens AI. Answer based on context. Be concise and helpful."""
        )
        prompt = f"<question>{query}</question>\n\n<context>\n{context}\n</context>"

        yield "data: Starting response...\n\n"

        full_response = ""
        async for chunk in llm_service.generate_streaming(prompt, system_prompt):
            if chunk.text:
                full_response += chunk.text
                yield f"data: {json.dumps({'content': chunk.text})}\n\n"

        yield f"data: {json.dumps({'done': True, 'sources_count': len(results)})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def _build_context(results: list, max_chunks: int) -> str:
    """Build context string from search results."""
    context_parts = []
    current_length = 0
    max_chars = 10000

    for result in results[:max_chunks]:
        if current_length + len(result.content) > max_chars:
            remaining = max_chars - current_length
            if remaining > 100:
                context_parts.append(result.content[:remaining] + "...")
            break

        source_info = ""
        if result.metadata.get("page"):
            source_info = f" [Page {result.metadata['page']}]"

        context_parts.append(
            f"<context id='{result.result_id}'>{source_info}\n{result.content}</context>"
        )
        current_length += len(result.content) + 100

    return "\n\n".join(context_parts)


import hashlib
