# DocuLens AI - Production-Ready Document Analysis Platform

> **Intelligent Document Analysis API** — Powered by FastAPI, Gemini AI, and Pinecone Vector Database

![Version](https://img.shields.io/badge/Version-3.1.0-009688?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Project Structure](#project-structure)
9. [RAG System](#rag-system)
10. [Security](#security)
11. [Performance](#performance)
12. [Troubleshooting](#troubleshooting)

---

## Overview

DocuLens AI is a **production-ready FastAPI service** that provides intelligent document analysis with:

- **Multi-format support**: PDF, DOCX, and Images (via OCR)
- **AI-powered analysis**: Summary generation, entity extraction, sentiment analysis
- **RAG capabilities**: Semantic search and question answering over documents
- **Modular architecture**: Clean separation of concerns for scalability

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Document Analysis** | Extract summary, entities, and sentiment from documents |
| **Entity Extraction** | Identify persons, organizations, dates, locations, monetary values |
| **Sentiment Analysis** | Classify document sentiment as positive/negative/neutral |
| **RAG Q&A** | Ask questions in natural language with source citations |
| **Semantic Search** | Find content by meaning, not just keywords |
| **Async Processing** | Non-blocking document processing |

### Supported Formats

| Format | Handler | Description |
|--------|---------|-------------|
| PDF | PyMuPDF + pdfplumber | Text extraction with layout preservation |
| DOCX | python-docx | Paragraph and table extraction |
| Images | Tesseract/EasyOCR | OCR-based text extraction |
| Text | Built-in | Plain text processing |

### Analysis Output

The `/analyze` endpoint returns a structured JSON response:

```json
{
  "status": "success",
  "document_id": "abc123def456",
  "summary": "A concise 150-word summary of the document...",
  "entities": {
    "persons": ["John Smith", "Jane Doe"],
    "organizations": ["Acme Corp", "Tech Inc"],
    "dates": ["January 15, 2024", "March 2024"],
    "locations": ["New York", "San Francisco"],
    "monetary_values": ["$50,000", "$1.2M"]
  },
  "sentiment": "neutral",
  "metadata": {
    "file_type": "pdf",
    "processing_time": "1.25s",
    "num_pages": "5"
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│  Web App │ Mobile App │ CLI │ Third-party Integrations          │
└────────────────────────────┬────────────────────────────────────┘
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (uvicorn)                  │
├─────────────────────────────────────────────────────────────────┤
│  Authentication Layer                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ API Key     │  │ Rate Limit  │  │ CORS        │            │
│  │ Validation  │  │ Checking    │  │ Middleware  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  API Endpoints (v1)                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ /analyze    │  │ /documents  │  │ /rag        │            │
│  │ Analysis    │  │ Ingestion   │  │ Q&A         │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  Services Layer (Modular Components)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Processing  │  │ Embedding   │  │ LLM         │            │
│  │ Service     │  │ Service     │  │ Service     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Vector      │  │ Document    │  │ Cache       │            │
│  │ Store       │  │ Service     │  │ Service     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                              │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                   ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  Pinecone   │   │   Gemini    │   │   Redis     │
    │  (Vectors)  │   │   (LLM)     │   │   (Cache)   │
    └─────────────┘   └─────────────┘   └─────────────┘
```

### Component Flow (Document Analysis)

```
Upload File
    │
    ▼
┌──────────────────┐
│ File Validation  │ ← FileProcessor.validate_file()
└────────┬─────────┘
         │
    ┌────▼─────────────┐
    │ Type Detection   │ ← PDF/DOCX/Image detection
    └────────┬─────────┘
         │
    ┌────▼──────────────────┐
    │ Text Extraction       │ ← PDF/DOCX/Image processors
    │ • PyMuPDF (PDF)       │
    │ • python-docx (DOCX)  │
    │ • Tesseract (OCR)     │
    └────────┬───────────────┘
         │
    ┌────▼─────────────────────┐
    │ Text Preprocessing       │ ← Clean and normalize
    └────────┬─────────────────┘
         │
    ┌────▼─────────────────────┐
    │ AI Processing             │ ← LLM + Fallback
    │ • Summary Generation      │
    │ • Entity Extraction      │
    │ • Sentiment Analysis      │
    └────────┬─────────────────┘
         │
    ┌────▼─────────────┐
    │ JSON Response    │
    └──────────────────┘
```

---

## API Endpoints

### Document Analysis

#### POST /v1/analyze

Analyze a document file (PDF, DOCX, or Image) and extract summary, entities, and sentiment.

**Authentication**: Required (X-API-Key header)

**Request**:

```bash
curl -X POST "http://localhost:8000/v1/analyze" \
  -H "X-API-Key: your-api-key" \
  -F "file=@document.pdf"
```

**Response**:

```json
{
  "status": "success",
  "document_id": "abc123def456",
  "summary": "This document discusses...",
  "entities": {
    "persons": ["John Smith"],
    "organizations": ["Acme Corp"],
    "dates": ["January 15, 2024"],
    "locations": ["New York"],
    "monetary_values": ["$50,000"]
  },
  "sentiment": "neutral",
  "metadata": {
    "file_type": "pdf",
    "processing_time": "1.25s",
    "num_pages": "5"
  }
}
```

#### POST /v1/analyze/text

Analyze raw text content directly.

**Authentication**: Required (X-API-Key header)

```bash
curl -X POST "http://localhost:8000/v1/analyze/text" \
  -H "X-API-Key: your-api-key" \
  -F "text=Your document text here..."
```

### Document Ingestion (RAG)

#### POST /v1/documents/ingest

Ingest a document for RAG retrieval.

```bash
curl -X POST "http://localhost:8000/v1/documents/ingest" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Document content...",
    "filename": "document.pdf",
    "file_type": "application/pdf"
  }'
```

#### POST /v1/rag/query

Query the document knowledge base.

```bash
curl -X POST "http://localhost:8000/v1/rag/query" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main contract terms?"
  }'
```

### Health Check

#### GET /health

```bash
curl "http://localhost:8000/health"
```

**Response**:

```json
{
  "status": "healthy",
  "service": "DocuLens AI",
  "version": "3.1.0",
  "features": {
    "rag": true,
    "cache": true,
    "streaming": true
  }
}
```

---

## Installation

### Prerequisites

- **Python 3.11+**
- **API Keys** (see Configuration section)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-repo/document-analyzer
cd document-analyzer/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Docker Setup

```bash
# Build and run with Docker
docker-compose up -d

# Or manually
docker build -t doculens-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=... doculens-backend
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Application
APP_NAME=DocuLens AI
APP_VERSION=3.1.0
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security (REQUIRED for production)
API_KEY=your-secure-api-key-here

# Gemini AI (REQUIRED for AI features)
GEMINI_API_KEY=your-gemini-api-key

# Pinecone Vector Database (REQUIRED for RAG)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=doculens-production
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Embedding Provider (gemini, openai, local)
EMBEDDING_PROVIDER=gemini

# OpenAI (alternative to Gemini)
OPENAI_API_KEY=your-openai-api-key

# Redis Cache (optional, for performance)
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true

# Document Processing
MAX_FILE_SIZE_MB=50
SUPPORTED_FILE_TYPES=pdf,docx,txt,png,jpg,jpeg

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# CORS
CORS_ORIGINS=*
```

### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_KEY` | string | - | API key for authentication |
| `GEMINI_API_KEY` | string | - | Google Gemini API key |
| `PINECONE_API_KEY` | string | - | Pinecone vector DB API key |
| `EMBEDDING_PROVIDER` | enum | gemini | Embedding provider (gemini/openai/local) |
| `MAX_FILE_SIZE_MB` | int | 50 | Maximum upload file size |
| `CHUNK_SIZE` | int | 1000 | Text chunk size for RAG |
| `CHUNK_OVERLAP` | int | 200 | Overlap between chunks |
| `REDIS_URL` | string | redis://localhost:6379/0 | Redis connection URL |

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_analyze.py -v

# Run with specific marker
pytest -m integration
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full pipeline testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test document analysis
curl -X POST "http://localhost:8000/v1/analyze" \
  -H "X-API-Key: your-api-key" \
  -F "file=@test.pdf"

# Access API documentation
open http://localhost:8000/docs
```

---

## Project Structure

```
document-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── analyze.py      # POST /analyze endpoint
│   │   │       │   ├── documents.py    # Document ingestion
│   │   │       │   ├── rag.py          # RAG Q&A
│   │   │       │   └── analysis.py     # Advanced analysis
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py               # Configuration management
│   │   │   ├── security.py             # API key auth, rate limiting
│   │   │   └── logging.py              # Logging setup
│   │   ├── models/
│   │   │   └── schemas.py              # Pydantic models
│   │   ├── services/
│   │   │   ├── processing/             # Document processing
│   │   │   │   ├── file_processor.py  # Unified file handler
│   │   │   │   ├── pdf_processor.py   # PDF extraction
│   │   │   │   ├── docx_processor.py  # DOCX extraction
│   │   │   │   ├── image_processor.py # OCR/Image extraction
│   │   │   │   ├── ai_processing.py   # Summary, NER, Sentiment
│   │   │   │   └── text_preprocessing.py
│   │   │   ├── document/               # Document service
│   │   │   ├── embedding/              # Embedding service
│   │   │   ├── vector/                 # Pinecone vector store
│   │   │   ├── llm/                    # Gemini LLM service
│   │   │   └── cache/                  # Redis cache
│   │   └── main.py                     # Application entry point
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

### Modular Components

#### 1. Document Processing (`app/services/processing/`)

- **file_processor.py**: Unified interface for all file types
- **pdf_processor.py**: PyMuPDF-based PDF extraction
- **docx_processor.py**: python-docx-based DOCX extraction
- **image_processor.py**: Tesseract/EasyOCR-based OCR
- **ai_processing.py**: Summary, entity extraction, sentiment
- **text_preprocessing.py**: Text cleaning and normalization

#### 2. RAG System (`app/services/`)

- **embedding/**: Multi-provider embedding (Gemini/OpenAI/Local)
- **vector/**: Pinecone vector database integration
- **document/**: Document chunking and ingestion

#### 3. Core Services

- **llm/**: Gemini LLM integration
- **cache/**: Redis caching for embeddings

---

## RAG System

The RAG (Retrieval-Augmented Generation) system is fully preserved and integrated:

### How It Works

1. **Document Ingestion**: Text is chunked and embedded
2. **Vector Storage**: Chunks stored in Pinecone
3. **Query Processing**: Query embedded and compared to vectors
4. **Context Retrieval**: Top-k similar chunks retrieved
5. **Answer Generation**: LLM generates answer with context

### RAG Endpoints

```bash
# Ingest document
POST /v1/documents/ingest

# Query with RAG
POST /v1/rag/query

# Semantic search
POST /v1/rag/search
```

### Configuration

RAG behavior can be tuned via environment variables:

- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of results to retrieve (default: 5)
- `EMBEDDING_PROVIDER`: Embedding model choice

---

## Security

### API Key Authentication

All production endpoints require API key authentication:

```bash
curl -H "X-API-Key: your-api-key" ...
```

### Rate Limiting

- Default: 100 requests per 60 seconds
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`

### Input Validation

- File type validation (PDF, DOCX, images only)
- File size limits (default: 50MB)
- Content type checking

### Security Best Practices

- API keys stored in environment variables (never in code)
- Secrets hashed using SHA-256
- CORS configured for allowed origins
- Input sanitization on all endpoints

---

## Performance

### Benchmarks

| Operation | Typical Time |
|-----------|-------------|
| Document upload | 1-2s per page |
| Text extraction | <500ms per page |
| AI analysis | 2-5s |
| Semantic search | <100ms |
| Cache hit | <10ms |

### Optimization Tips

1. **Enable Redis cache** for faster embedding lookups
2. **Use async processing** for better concurrency
3. **Configure chunk sizes** based on document type
4. **Monitor with /health endpoint**

---

## Troubleshooting

### Common Issues

#### 1. No text extracted from PDF

**Cause**: Encrypted or scanned PDF
**Solution**: Ensure PDF is text-based or use OCR-enabled processing

#### 2. API key authentication failing

**Cause**: Incorrect or missing API key
**Solution**: Verify `API_KEY` in `.env` and header in request

#### 3. RAG queries returning empty results

**Cause**: No documents ingested
**Solution**: Ingest documents first using `/v1/documents/ingest`

#### 4. LLM features not working

**Cause**: Missing or invalid Gemini API key
**Solution**: Verify `GEMINI_API_KEY` in `.env`

#### 5. OCR not working on images

**Cause**: Tesseract not installed
**Solution**: Install Tesseract OCR or EasyOCR

### Error Responses

```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file, empty text)
- `401`: Unauthorized (invalid/missing API key)
- `413`: File too large
- `429`: Rate limit exceeded
- `500`: Internal server error

---

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## License

MIT License - see LICENSE file for details.

---

## Acknowledgments

- **Google** for Gemini AI and embeddings
- **Pinecone** for vector database
- **FastAPI** for the async Python framework
- **PyMuPDF** for PDF processing
- **Tesseract** for OCR capabilities

---

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section

---

<div align="center">
  <strong>Built with ❤️ for Production</strong>
  <br>
  <sub>DocuLens AI - Your Intelligent Document Analysis Platform</sub>
</div>
