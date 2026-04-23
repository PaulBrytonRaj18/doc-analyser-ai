# DocuLens AI — Intelligent Document Intelligence Platform

> **Advanced OCR · RAG · Real-time Analysis** — Powered by FastAPI, Gemini AI, Pinecone, and OpenCV

![Version](https://img.shields.io/badge/Version-4.0.0-7C3AED?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-06B6D4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![Gemini](https://img.shields.io/badge/Gemini_AI-Pro-4285F4?style=for-the-badge&logo=google)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-10B981?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Table of Contents

1. [Overview](#overview)
2. [What's New in v4.0](#whats-new-in-v40)
3. [Architecture](#architecture)
4. [Core Feature Modules](#core-feature-modules)
   - [OCR Pipeline](#1-ocr-pipeline--photo-document-scanning)
   - [Auto-Analysis Engine](#2-auto-analysis-engine)
   - [RAG System](#3-rag-system--conversational-qa)
   - [Document Intelligence](#4-document-intelligence-features)
5. [API Endpoints](#api-endpoints)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Project Structure](#project-structure)
9. [Security](#security)
10. [Performance](#performance)
11. [Webhooks & Events](#webhooks--events)
12. [Troubleshooting](#troubleshooting)
13. [Color Palette & Design System](#color-palette--design-system)

---

## Overview

**DocuLens AI v4.0** is a production-grade document intelligence platform engineered around three core pillars:

- **Smart OCR Ingestion** — Upload photos of physical documents (receipts, contracts, handwritten notes, skewed scans). The preprocessing pipeline auto-corrects orientation, removes noise, and enhances contrast before OCR extraction, delivering high-accuracy text even from imperfect camera captures.
- **Instant Auto-Analysis** — The moment a document is uploaded, a background pipeline triggers automatically: classification, summary, entity extraction, sentiment scoring, and key-insight tagging — all returned before you even ask a question.
- **Conversational RAG Q&A** — Ask natural language questions over single or multiple documents simultaneously. Responses include pinpoint source citations (page number, bounding box, or chunk reference), confidence scores, and follow-up question suggestions.

**Tech Stack**: FastAPI · Gemini AI (LLM + Embeddings) · Pinecone (Vector DB) · Redis (Cache + Job Queue) · OpenCV (Image Preprocessing) · Tesseract + EasyOCR · PyMuPDF · Celery

---

## What's New in v4.0

| Feature | v3.1 | v4.0 |
|---|---|---|
| Photo-taken document OCR | Basic | Advanced pipeline with deskew, denoise, binarization |
| Auto-analysis on upload | Manual trigger | Fully automatic, streaming response |
| OCR confidence scoring | No | Yes — per-word and per-region |
| Handwriting recognition | No | Yes — via EasyOCR handwriting model |
| Multi-document RAG | No | Yes — cross-document Q&A |
| Document classification | No | Yes — 12 document types |
| Table extraction from images | No | Yes — structured JSON output |
| Named entity redaction | No | Yes — PII anonymization endpoint |
| Document comparison | No | Yes — semantic diff between two documents |
| Batch processing | No | Yes — up to 50 documents per job |
| Webhook notifications | No | Yes — lifecycle events |
| Streaming responses | Partial | Full SSE streaming on all analysis endpoints |
| Export formats | JSON only | JSON · CSV · PDF Report · Markdown |
| Audit logging | No | Yes — per-request tamper-evident log |
| Multi-language OCR | No | Yes — 40+ languages |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Client Applications                              │
│   Web App  │  Mobile App  │  CLI  │  Webhooks  │  Third-party SDKs       │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │ HTTPS / SSE / WebSocket
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Gateway (uvicorn)                          │
├────────────────────────────────────────────────────────────────┬─────────┤
│  Auth & Middleware Layer                                        │         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │ OpenAPI │
│  │  API Key     │  │  Rate Limit  │  │  CORS +      │         │  /docs  │
│  │  Validation  │  │  (Redis)     │  │  Audit Log   │         │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │         │
├────────────────────────────────────────────────────────────────┴─────────┤
│  API Router (v1)                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ /upload  │  │ /analyze │  │ /rag     │  │ /ocr     │  │ /export  │  │
│  │ Ingest   │  │ Auto     │  │ Q&A      │  │ Scan     │  │ Reports  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                               │
│  │ /compare │  │ /batch   │  │ /redact  │                               │
│  │ Diff     │  │ Bulk Job │  │ PII Mask │                               │
│  └──────────┘  └──────────┘  └──────────┘                               │
├──────────────────────────────────────────────────────────────────────────┤
│  Services Layer                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  OCR Pipeline   │  │  Analysis       │  │  RAG Engine     │          │
│  │  • OpenCV Prep  │  │  Engine         │  │  • Chunker      │          │
│  │  • Deskew       │  │  • Classifier   │  │  • Embedder     │          │
│  │  • Denoise      │  │  • Summarizer   │  │  • Retriever    │          │
│  │  • Tesseract    │  │  • NER          │  │  • Generator    │          │
│  │  • EasyOCR      │  │  • Sentiment    │  │  • Citer        │          │
│  │  • Confidence   │  │  • Insights     │  │                 │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Document Store │  │  LLM Service    │  │  Export Service │          │
│  │  • Metadata     │  │  • Gemini Pro   │  │  • PDF Report   │          │
│  │  • Versioning   │  │  • Streaming    │  │  • CSV / JSON   │          │
│  │  • Comparison   │  │  • Fallback     │  │  • Markdown     │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
          ┌──────────┬─────────────┼──────────────┬──────────────┐
          ▼          ▼             ▼               ▼              ▼
   ┌───────────┐ ┌────────┐ ┌──────────┐  ┌──────────────┐ ┌─────────┐
   │ Pinecone  │ │ Gemini │ │  Redis   │  │   Celery     │ │ Postgres│
   │ (Vectors) │ │  (LLM) │ │ (Cache + │  │ (Background  │ │ (Meta + │
   │           │ │        │ │  Queue)  │  │  Jobs)       │ │  Audit) │
   └───────────┘ └────────┘ └──────────┘  └──────────────┘ └─────────┘
```

### Upload & Auto-Analysis Flow

```
Upload File (Photo / PDF / DOCX / Image)
          │
          ▼
┌─────────────────────────┐
│  File Validation        │  ← Type, size, MIME check
│  + Virus Scan Hook      │
└────────────┬────────────┘
             │
     ┌───────▼──────────────┐
     │ File Type Router     │
     │  • Photo/Scan → OCR  │
     │  • PDF → PyMuPDF     │
     │  • DOCX → python-docx│
     └───────┬──────────────┘
             │
     ┌───────▼──────────────────────────────┐
     │  OCR Pre-Processing Pipeline         │  ← (Images & Scanned PDFs only)
     │  1. Grayscale conversion             │
     │  2. Adaptive thresholding            │
     │  3. Deskew (Hough transform)         │
     │  4. Denoising (FastNlMeans)          │
     │  5. Contrast enhancement (CLAHE)     │
     │  6. Border removal                   │
     └───────┬──────────────────────────────┘
             │
     ┌───────▼──────────────────────────────┐
     │  OCR Extraction                      │
     │  • Tesseract (printed text)          │
     │  • EasyOCR (handwriting / degraded)  │
     │  • Confidence score per word/region  │
     │  • Bounding box coordinates          │
     │  • Language auto-detection           │
     └───────┬──────────────────────────────┘
             │
     ┌───────▼────────────────────┐
     │  Text Preprocessing        │  ← Clean, normalize, deduplicate
     └───────┬────────────────────┘
             │
    ┌────────▼────────────────────────────────────────┐
    │  Auto-Analysis Engine  (fires automatically)    │
    │  ┌──────────────┐  ┌──────────────┐             │
    │  │ Document     │  │ Summarizer   │             │
    │  │ Classifier   │  │ (Gemini Pro) │             │
    │  └──────────────┘  └──────────────┘             │
    │  ┌──────────────┐  ┌──────────────┐             │
    │  │ Named Entity │  │ Sentiment +  │             │
    │  │ Recognition  │  │ Key Insights │             │
    │  └──────────────┘  └──────────────┘             │
    │  ┌──────────────┐  ┌──────────────┐             │
    │  │ Table        │  │ PII Detection│             │
    │  │ Extraction   │  │ (flag only)  │             │
    │  └──────────────┘  └──────────────┘             │
    └────────┬────────────────────────────────────────┘
             │
     ┌───────▼────────────────────┐
     │  RAG Ingestion             │  ← Auto-chunk, embed, upsert to Pinecone
     │  (runs in parallel)        │
     └───────┬────────────────────┘
             │
     ┌───────▼────────────────────┐
     │  Webhook Dispatch          │  ← Fires `document.ready` event
     └───────┬────────────────────┘
             │
     ┌───────▼────────────────────┐
     │  Streaming JSON Response   │  ← SSE stream with partial results
     └────────────────────────────┘
```

---

## Core Feature Modules

### 1. OCR Pipeline — Photo Document Scanning

DocuLens v4.0 treats camera-captured images as first-class citizens. The preprocessing chain runs before any OCR engine touches the image:

**Image Preprocessing Steps**

```
Raw Photo
    │
    ├─► Grayscale Conversion
    ├─► Adaptive Thresholding (handles uneven lighting from flash/shadow)
    ├─► Deskew — Hough Line Transform corrects tilt up to ±45°
    ├─► Denoising — FastNlMeansDenoising (preserves edge sharpness)
    ├─► CLAHE — Contrast Limited Adaptive Histogram Equalization
    ├─► Border Cropping — Removes camera frame noise
    └─► Preprocessed Image → OCR Engine
```

**OCR Confidence Response**

```json
{
  "document_id": "doc_7f3a21bc",
  "ocr_result": {
    "full_text": "Invoice #INV-2024-0091\nDate: March 5, 2024...",
    "language_detected": "en",
    "overall_confidence": 0.947,
    "regions": [
      {
        "region_id": 1,
        "text": "Invoice #INV-2024-0091",
        "confidence": 0.991,
        "bounding_box": { "x": 42, "y": 18, "width": 310, "height": 28 },
        "engine_used": "tesseract"
      },
      {
        "region_id": 2,
        "text": "Handwritten note: approved by J.K.",
        "confidence": 0.831,
        "bounding_box": { "x": 10, "y": 580, "width": 260, "height": 22 },
        "engine_used": "easyocr_handwriting"
      }
    ],
    "low_confidence_regions": [2],
    "preprocessing_applied": ["grayscale", "deskew", "denoise", "clahe"]
  }
}
```

**Supported Input**

| Source | Formats | Notes |
|--------|---------|-------|
| Camera capture | JPG, HEIC, WEBP, PNG | Auto-deskew up to ±45° |
| Scanned documents | TIFF, PNG, BMP | 300 DPI recommended |
| PDF (scanned) | PDF | Rasterized per-page before OCR |
| PDF (digital) | PDF | Text layer extracted directly |
| Word documents | DOCX | python-docx extraction |
| Plain text | TXT, MD | Passthrough |

**Languages Supported**: 40+ via Tesseract language packs, including Tamil, Hindi, Arabic, Chinese, Japanese, and all major European languages.

---

### 2. Auto-Analysis Engine

Every upload triggers a full analysis pipeline automatically — no separate API call required. Results stream back via Server-Sent Events (SSE) as each stage completes.

**Document Classification** (12 categories)

```
invoice · contract · receipt · report · resume · legal_filing ·
medical_record · id_document · handwritten_note · form · academic · general
```

**Full Auto-Analysis Response**

```json
{
  "status": "success",
  "document_id": "doc_7f3a21bc",
  "classification": {
    "type": "invoice",
    "confidence": 0.96,
    "sub_type": "commercial_invoice"
  },
  "summary": "A commercial invoice issued by Acme Corp to Tech Inc for software licensing services totalling $12,400, dated March 5, 2024, with payment due April 4, 2024.",
  "key_insights": [
    "Payment due in 30 days",
    "Late fee clause detected: 1.5% per month",
    "GST/Tax line item present"
  ],
  "entities": {
    "persons": ["Jane Doe", "John Smith"],
    "organizations": ["Acme Corp", "Tech Inc"],
    "dates": ["March 5, 2024", "April 4, 2024"],
    "locations": ["San Francisco, CA"],
    "monetary_values": ["$12,400", "$186.00 (tax)"],
    "invoice_numbers": ["INV-2024-0091"],
    "email_addresses": ["billing@acmecorp.com"]
  },
  "sentiment": {
    "label": "neutral",
    "score": 0.02
  },
  "tables_extracted": [
    {
      "table_id": 1,
      "headers": ["Item", "Qty", "Unit Price", "Total"],
      "rows": [
        ["Software License - Enterprise", "1", "$12,400.00", "$12,400.00"]
      ]
    }
  ],
  "pii_detected": true,
  "pii_types": ["email_address", "person_name"],
  "metadata": {
    "file_type": "image/jpeg",
    "ocr_confidence": 0.947,
    "processing_time_ms": 2840,
    "pages": 1,
    "word_count": 312
  }
}
```

---

### 3. RAG System — Conversational Q&A

**Single & Multi-Document Q&A**

Ask questions across a single document or an entire collection. The retriever finds the most semantically relevant chunks and the LLM generates a grounded answer with source citations.

```bash
# Single document Q&A
POST /v1/rag/query
{
  "query": "What are the payment terms?",
  "document_id": "doc_7f3a21bc"
}

# Multi-document Q&A (cross-document reasoning)
POST /v1/rag/query
{
  "query": "Compare the payment terms across all uploaded invoices",
  "document_ids": ["doc_7f3a21bc", "doc_9a1b2c3d", "doc_4e5f6a7b"]
}
```

**RAG Response with Citations**

```json
{
  "answer": "The payment terms specify that invoices are due within 30 days of the invoice date. A late fee of 1.5% per month applies to overdue balances, as stated in clause 4.2.",
  "confidence": 0.93,
  "sources": [
    {
      "document_id": "doc_7f3a21bc",
      "chunk_id": "chunk_14",
      "page": 1,
      "region": { "x": 42, "y": 480, "width": 510, "height": 44 },
      "excerpt": "...payment is due within thirty (30) days of invoice date...",
      "relevance_score": 0.961
    }
  ],
  "follow_up_suggestions": [
    "What is the total amount due including late fees?",
    "Is there an early payment discount?",
    "Who is the billing contact for disputes?"
  ]
}
```

**RAG Configuration**

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | 800 | Tokens per chunk |
| `CHUNK_OVERLAP` | 150 | Overlap between chunks |
| `TOP_K_RESULTS` | 6 | Retrieved chunks per query |
| `MIN_RELEVANCE_SCORE` | 0.65 | Minimum cosine similarity threshold |
| `EMBEDDING_PROVIDER` | `gemini` | `gemini` / `openai` / `local` |
| `RERANK_ENABLED` | `true` | Cross-encoder reranking of retrieved chunks |

---

### 4. Document Intelligence Features

**Document Comparison (Semantic Diff)**

```bash
POST /v1/compare
{
  "document_id_a": "doc_7f3a21bc",
  "document_id_b": "doc_9a1b2c3d",
  "focus": "payment_terms"   # optional: narrows the diff scope
}
```

Response highlights added, removed, and changed sections with a semantic similarity score between the two documents.

**PII Redaction**

```bash
POST /v1/redact
{
  "document_id": "doc_7f3a21bc",
  "pii_types": ["person_name", "email_address", "phone_number"],
  "replacement": "[REDACTED]"
}
```

Returns a new document with identified PII replaced. The original is preserved unless `overwrite: true` is passed.

**Batch Processing**

```bash
POST /v1/batch/upload
Content-Type: multipart/form-data

files[]: contract_a.pdf
files[]: invoice_001.jpg
files[]: receipt_scan.png
...  (up to 50 files)
```

Returns a `batch_id`. Poll `GET /v1/batch/{batch_id}/status` or receive results via webhook when all jobs complete.

**Export**

```bash
# Export analysis report as PDF
GET /v1/documents/{document_id}/export?format=pdf_report

# Export entities as CSV
GET /v1/documents/{document_id}/export?format=csv

# Export full analysis as Markdown
GET /v1/documents/{document_id}/export?format=markdown
```

---

## API Endpoints

### Upload & Ingestion

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/upload` | Upload file → triggers auto-analysis + RAG ingestion |
| `POST` | `/v1/upload/stream` | Upload with SSE streaming of analysis stages |
| `POST` | `/v1/batch/upload` | Upload up to 50 files as a batch job |
| `GET`  | `/v1/documents` | List all ingested documents |
| `GET`  | `/v1/documents/{id}` | Retrieve document metadata & analysis |
| `DELETE` | `/v1/documents/{id}` | Delete document and its vectors |

### OCR

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/ocr/scan` | OCR a photo/image, returns text + confidence |
| `POST` | `/v1/ocr/scan/preview` | Returns preprocessed image + OCR overlay (for UI debugging) |
| `POST` | `/v1/ocr/languages` | Detect language in an image |

### Analysis

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/v1/analyze/{document_id}` | Retrieve cached auto-analysis result |
| `POST` | `/v1/analyze/text` | Analyze raw text (no file upload) |
| `POST` | `/v1/compare` | Semantic diff between two documents |
| `POST` | `/v1/redact` | PII redaction on a stored document |

### RAG & Search

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/rag/query` | Natural language Q&A (single or multi-document) |
| `POST` | `/v1/rag/search` | Semantic chunk search without generation |
| `GET`  | `/v1/rag/history/{document_id}` | Retrieve Q&A history for a document |

### Export & Reporting

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/v1/documents/{id}/export` | Export analysis (pdf_report, csv, json, markdown) |
| `GET`  | `/v1/batch/{batch_id}/export` | Export all results from a batch job |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Service health + dependency status |
| `GET`  | `/v1/audit/logs` | Tamper-evident audit log (admin only) |
| `GET`  | `/docs` | Swagger UI |
| `GET`  | `/redoc` | ReDoc |

---

## Installation

### Prerequisites

- **Python 3.11+**
- **Tesseract OCR** (`apt install tesseract-ocr tesseract-ocr-[lang]`)
- **OpenCV system libs** (`apt install libgl1`)
- **Redis 7+**
- **PostgreSQL 15+**
- API Keys: Gemini AI, Pinecone

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-repo/doculens-ai
cd doculens-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract language packs (example: English + Tamil)
sudo apt-get install tesseract-ocr-eng tesseract-ocr-tam

# Set up environment
cp .env.example .env
# Edit .env with your API keys and DB connection strings

# Run database migrations
alembic upgrade head

# Start Redis (if not running)
redis-server &

# Start Celery worker (background job processor)
celery -A app.worker worker --loglevel=info &

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Compose (Recommended)

```bash
cp .env.example .env
# Edit .env

docker compose up --build
```

Services started: `api`, `celery_worker`, `redis`, `postgres`

---

## Configuration

### Environment Variables

```env
# ─── Core ───────────────────────────────────────────────────────
APP_ENV=production
API_KEY=your-secret-api-key
SECRET_KEY=your-jwt-secret

# ─── Gemini AI ──────────────────────────────────────────────────
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro

# ─── Pinecone ───────────────────────────────────────────────────
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX=doculens-vectors
PINECONE_REGION=us-east-1

# ─── Redis ──────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ─── PostgreSQL ─────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/doculens

# ─── OCR ────────────────────────────────────────────────────────
OCR_ENGINE=auto                     # auto | tesseract | easyocr
OCR_DEFAULT_LANGUAGE=eng
OCR_CONFIDENCE_THRESHOLD=0.70       # Low-confidence regions flagged
PREPROCESSING_ENABLED=true
DESKEW_MAX_ANGLE=45

# ─── RAG ────────────────────────────────────────────────────────
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K_RESULTS=6
MIN_RELEVANCE_SCORE=0.65
RERANK_ENABLED=true
EMBEDDING_PROVIDER=gemini           # gemini | openai | local

# ─── File Handling ──────────────────────────────────────────────
MAX_FILE_SIZE_MB=100
BATCH_MAX_FILES=50
ALLOWED_EXTENSIONS=pdf,docx,txt,jpg,jpeg,png,tiff,webp,heic,bmp

# ─── Rate Limiting ──────────────────────────────────────────────
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW_SECONDS=60

# ─── Webhooks ───────────────────────────────────────────────────
WEBHOOK_SECRET=your-webhook-signing-secret
WEBHOOK_RETRY_ATTEMPTS=3

# ─── Security ───────────────────────────────────────────────────
CORS_ORIGINS=https://yourapp.com
PII_DETECTION_ENABLED=true
AUDIT_LOG_ENABLED=true
```

---

## Project Structure

```
doculens-ai/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── upload.py           # POST /upload, /upload/stream
│   │       │   ├── ocr.py              # POST /ocr/scan, /ocr/scan/preview
│   │       │   ├── analyze.py          # GET /analyze/{id}, POST /analyze/text
│   │       │   ├── rag.py              # POST /rag/query, /rag/search
│   │       │   ├── documents.py        # CRUD on stored documents
│   │       │   ├── compare.py          # POST /compare
│   │       │   ├── redact.py           # POST /redact
│   │       │   ├── batch.py            # POST /batch/upload, GET /batch/{id}
│   │       │   ├── export.py           # GET /documents/{id}/export
│   │       │   └── audit.py            # GET /audit/logs
│   │       └── router.py
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings
│   │   ├── security.py                 # API key auth, JWT, rate limit
│   │   ├── logging.py                  # Structured JSON logging
│   │   └── audit.py                    # Tamper-evident audit trail
│   ├── models/
│   │   ├── schemas.py                  # Pydantic I/O models
│   │   └── db.py                       # SQLAlchemy ORM models
│   ├── services/
│   │   ├── ocr/
│   │   │   ├── preprocessor.py         # OpenCV image preprocessing pipeline
│   │   │   ├── tesseract_engine.py     # Tesseract OCR wrapper
│   │   │   ├── easyocr_engine.py       # EasyOCR (handwriting) wrapper
│   │   │   ├── ocr_router.py           # Engine selection logic
│   │   │   └── confidence.py           # Per-word/region confidence scoring
│   │   ├── processing/
│   │   │   ├── file_processor.py       # Unified file type router
│   │   │   ├── pdf_processor.py        # PyMuPDF text + page extraction
│   │   │   ├── docx_processor.py       # python-docx extraction
│   │   │   └── text_preprocessing.py   # Clean, normalize, deduplicate
│   │   ├── analysis/
│   │   │   ├── classifier.py           # Document type classification
│   │   │   ├── summarizer.py           # Gemini-powered summarization
│   │   │   ├── ner.py                  # Named entity recognition
│   │   │   ├── sentiment.py            # Sentiment + tone scoring
│   │   │   ├── insights.py             # Key insight extraction
│   │   │   ├── table_extractor.py      # Table detection + JSON conversion
│   │   │   └── pii_detector.py         # PII type flagging
│   │   ├── rag/
│   │   │   ├── chunker.py              # Semantic text chunking
│   │   │   ├── embedder.py             # Multi-provider embedding
│   │   │   ├── retriever.py            # Pinecone similarity retrieval
│   │   │   ├── reranker.py             # Cross-encoder reranking
│   │   │   ├── generator.py            # Grounded answer generation
│   │   │   └── citer.py                # Source citation builder
│   │   ├── document/
│   │   │   ├── store.py                # Document CRUD + versioning
│   │   │   ├── comparator.py           # Semantic document diff
│   │   │   └── redactor.py             # PII masking & anonymization
│   │   ├── export/
│   │   │   ├── pdf_report.py           # PDF analysis report builder
│   │   │   ├── csv_exporter.py         # Entity/table CSV export
│   │   │   └── markdown_exporter.py    # Markdown export
│   │   ├── llm/
│   │   │   ├── gemini_client.py        # Gemini API client + streaming
│   │   │   └── fallback.py             # Graceful LLM fallback logic
│   │   ├── cache/
│   │   │   └── redis_cache.py          # Embedding + analysis cache
│   │   └── webhook/
│   │       └── dispatcher.py           # Webhook event dispatch + retry
│   ├── worker/
│   │   ├── celery_app.py               # Celery config
│   │   └── tasks/
│   │       ├── analyze_task.py         # Background auto-analysis task
│   │       ├── batch_task.py           # Batch processing task
│   │       └── ingest_task.py          # RAG ingestion task
│   └── main.py                         # FastAPI app + lifespan
├── migrations/                         # Alembic DB migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Security

**Authentication**: All endpoints require `X-API-Key` header. Admin endpoints additionally require a scoped JWT token.

**Rate Limiting**: Redis-backed sliding window limiter. Default: 200 requests/60s per API key. Configurable per key tier.

**Input Validation**: File type, MIME type, size, and filename sanitization on every upload. Malicious file detection hook available.

**PII Handling**: PII detection is non-destructive — originals are never modified unless `/v1/redact` is explicitly called with `overwrite: true`.

**Audit Logging**: Every request is logged to PostgreSQL with a SHA-256 chain hash (each entry includes the hash of the previous), making the log tamper-evident.

**Secrets Management**: All API keys sourced from environment variables. Secrets are hashed (SHA-256) before being stored in logs. Never committed to source control.

**CORS**: Restricted to `CORS_ORIGINS`. Wildcard (`*`) only permitted in `development` env.

---

## Performance

### Benchmarks

| Operation | Typical Time |
|-----------|-------------|
| Image preprocessing (OpenCV) | 80–200ms |
| OCR extraction (Tesseract) | 300–900ms per page |
| OCR extraction (EasyOCR) | 800ms–2s per page |
| Auto-analysis (full pipeline) | 3–6s |
| RAG ingestion (chunking + embed) | 1–3s per document |
| RAG query (retrieve + generate) | 1.5–3s |
| Semantic search only | <120ms |
| Cache hit (embedding) | <15ms |
| Batch job (50 docs) | ~2–4 min (Celery workers) |

### Optimization Tips

- Enable Redis embedding cache (`REDIS_URL` set) to avoid redundant embedding API calls.
- Use `upload/stream` endpoint for large files to deliver partial analysis results progressively.
- Tune `CHUNK_SIZE` and `TOP_K_RESULTS` to balance answer quality vs. latency.
- Scale Celery workers horizontally for batch workloads.
- Use `RERANK_ENABLED=false` if sub-second RAG latency is critical and precision can be relaxed.

---

## Webhooks & Events

Register a webhook URL via the API to receive lifecycle events:

```bash
POST /v1/webhooks/register
{
  "url": "https://yourapp.com/webhook",
  "events": ["document.ready", "batch.complete", "rag.query.done"]
}
```

**Available Events**

| Event | Fired When |
|-------|-----------|
| `document.ready` | Upload processed + auto-analysis complete |
| `document.failed` | Processing failed (includes error detail) |
| `batch.complete` | All files in a batch job have been processed |
| `batch.partial` | Some files completed, some failed |
| `rag.query.done` | Async RAG query finished |

All webhook payloads are signed with `HMAC-SHA256` using your `WEBHOOK_SECRET`. Failed deliveries are retried up to `WEBHOOK_RETRY_ATTEMPTS` times with exponential backoff.

---

## Troubleshooting

**OCR returns garbled text from a photo**
Cause: Poor lighting, extreme tilt, or very low resolution.
Solution: Ensure the image is at least 150 DPI equivalent. Enable `PREPROCESSING_ENABLED=true`. For severe cases, call `/v1/ocr/scan/preview` to inspect the preprocessed image.

**Auto-analysis takes more than 10 seconds**
Cause: Cold Gemini API, large document, or Celery worker not running.
Solution: Verify the Celery worker is active (`celery inspect active`). Use streaming endpoint `/v1/upload/stream` for progressive results during processing.

**RAG returns low-quality answers**
Cause: `MIN_RELEVANCE_SCORE` too low, or document not ingested.
Solution: Raise `MIN_RELEVANCE_SCORE` to `0.72+`. Check `/v1/documents/{id}` to confirm `rag_ingested: true`.

**Tesseract not found**
Cause: Tesseract binary missing from PATH.
Solution: `sudo apt-get install tesseract-ocr` and confirm with `tesseract --version`.

**Pinecone upsert errors**
Cause: Index dimension mismatch with embedding model.
Solution: Ensure Pinecone index was created with the correct dimension for your `EMBEDDING_PROVIDER` (Gemini: 768, OpenAI text-embedding-3-small: 1536).

**PII detected but redaction endpoint not removing all instances**
Cause: Low-confidence OCR regions may produce variant spellings.
Solution: Set `OCR_CONFIDENCE_THRESHOLD=0.60` to expand OCR capture, then re-run redaction.

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `202` | Accepted (async job queued) |
| `400` | Bad request |
| `401` | Invalid / missing API key |
| `413` | File too large |
| `415` | Unsupported file type |
| `422` | Validation error |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

---

## Color Palette & Design System

The following palette is recommended for any frontend built on top of this API. It is designed to communicate trust, precision, and intelligence — the three qualities users expect from a document analysis tool.

### Recommended Palette

**Background Tier**

| Role | Name | Hex |
|------|------|-----|
| App background | Midnight Navy | `#0B1120` |
| Card / panel background | Deep Space | `#111827` |
| Input / code block background | Slate Well | `#1E293B` |
| Dividers / borders | Steel | `#334155` |

**Brand & Actions**

| Role | Name | Hex |
|------|------|-----|
| Primary brand / CTA buttons | Electric Violet | `#7C3AED` |
| Hover state | Deep Violet | `#6D28D9` |
| Secondary accent (links, highlights) | Cyan Pulse | `#06B6D4` |
| Active selection / focus ring | Vivid Indigo | `#818CF8` |

**Semantic / Feedback**

| Role | Name | Hex |
|------|------|-----|
| Success / high confidence | Emerald | `#10B981` |
| Warning / medium confidence | Amber | `#F59E0B` |
| Error / low confidence | Rose | `#F43F5E` |
| Info / neutral state | Sky | `#38BDF8` |

**Typography**

| Role | Name | Hex |
|------|------|-----|
| Primary text | Snow White | `#F8FAFC` |
| Secondary text | Cool Slate | `#94A3B8` |
| Muted / disabled | Steel Mist | `#64748B` |
| Code / monospace | Soft Green | `#A3E635` |

### Why This Palette Works for Document Intelligence

The dark navy base creates a neutral, high-contrast canvas that makes scanned documents and extracted text the visual hero of the interface. Electric Violet (`#7C3AED`) is bold enough to serve as a clear call-to-action without the corporate blandness of blue — it signals AI-powered sophistication. Cyan Pulse (`#06B6D4`) maps well to OCR scanning UX (think laser-line animations). The Emerald / Amber / Rose trio gives instant, intuitive confidence-score feedback without requiring the user to read numbers.

### OCR Confidence Color Mapping

```
≥ 0.90  →  Emerald   #10B981   High confidence, display as-is
0.70–0.89 → Amber    #F59E0B   Medium confidence, soft highlight
< 0.70  →  Rose      #F43F5E   Low confidence, flag for review
```

---

## License

MIT License — see `LICENSE` for full terms.

---

## Acknowledgments

- **Google** — Gemini Pro LLM and embedding API
- **Pinecone** — Vector database infrastructure
- **FastAPI** — Async Python web framework
- **OpenCV** — Image preprocessing pipeline
- **Tesseract OCR** — Printed text extraction engine
- **EasyOCR** — Handwriting and degraded document recognition
- **PyMuPDF** — PDF page rendering and text extraction
- **Celery** — Distributed background job processing

---

<div align="center">
  <strong>DocuLens AI v4.0 — See Everything Inside Your Documents</strong>
  <br>
  <sub>OCR · Auto-Analysis · Conversational RAG · Built for Production</sub>
</div>