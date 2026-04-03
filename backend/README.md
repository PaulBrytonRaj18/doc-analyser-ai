# DocuLens AI Backend

Production-ready FastAPI backend with RAG, synthesis, comparison, and insight extraction.

## Quick Start

```bash
cd backend

pip install -r requirements.txt

cp .env.example .env
# Configure: GEMINI_API_KEY, PINECONE_API_KEY

uvicorn app.main:app --reload
```

## API Endpoints

### Documents
- `POST /v1/documents/ingest` - Ingest document
- `POST /v1/documents/ingest/file` - Upload file
- `POST /v1/documents/ingest/batch` - Batch ingest
- `DELETE /v1/documents/{id}` - Delete document
- `POST /v1/documents/analyze` - Analyze document

### RAG
- `POST /v1/rag/query` - Query with RAG
- `POST /v1/rag/search` - Semantic search

### Analysis
- `POST /v1/analysis/synthesize` - Multi-doc synthesis
- `POST /v1/analysis/compare` - Compare documents
- `POST /v1/analysis/insights` - Extract insights

## Environment Variables

```env
GEMINI_API_KEY=your-key
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=doculens-production
```
