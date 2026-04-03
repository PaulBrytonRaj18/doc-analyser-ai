# 🏏 DocuLens AI

> **Intelligent Document Analysis Platform** — Powered by RAG, Gemini AI, and Pinecone Vector Database

![DocuLens AI](https://img.shields.io/badge/Version-3.0.0-D1122D?style=for-the-badge)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge)
![Gemini](https://img.shields.io/badge/AI-Gemini-4285F4?style=for-the-badge&logo=google)
![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-FF4D6D?style=for-the-badge)

---

## 🎯 What is DocuLens AI?

DocuLens AI is a **production-ready document intelligence platform** that transforms how organizations interact with their documents. Upload any document, and get instant AI-powered insights through:

- 💬 **Natural Language Q&A** with RAG-powered accuracy
- 📊 **Multi-Document Synthesis** combining information from 100s of docs
- ⚖️ **Document Comparison** finding similarities and conflicts
- 🔍 **Intelligent Insight Extraction** - action items, deadlines, risks

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **RAG Q&A** | Ask questions in natural language, get answers with source citations |
| **Semantic Search** | Find content by meaning, not just keywords |
| **Multi-Document Synthesis** | Combine insights from multiple documents |
| **Document Comparison** | Side-by-side analysis with similarity metrics |
| **Insight Extraction** | Auto-extract action items, decisions, deadlines, risks |
| **Real-time Streaming** | Watch AI generate responses in real-time |

### Supported Formats

- 📄 PDF documents
- 📝 Microsoft Word (DOCX)
- 📃 Plain text (TXT)
- 🖼️ Images with OCR (PNG, JPG)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  Dashboard │ Documents │ Chat │ Analysis │ Settings                │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  Documents API │ RAG API │ Analysis API                          │
├─────────────────────────────────────────────────────────────────┤
│  Services Layer                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Document │ │ Vector   │ │ Embedding│ │ LLM      │          │
│  │ Service  │ │ Store    │ │ Service  │ │ Service  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                   ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │  Pinecone   │   │   Gemini    │   │   Redis     │
   │  (Vectors)  │   │   (LLM)    │   │   (Cache)   │
   └─────────────┘   └─────────────┘   └─────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- API Keys:
  - [Gemini API Key](https://makersuite.google.com/app/apikey)
  - [Pinecone API Key](https://app.pinecone.io/)

### 1. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd document-analyzer

# Configure backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys:
# GEMINI_API_KEY=your_gemini_key
# PINECONE_API_KEY=your_pinecone_key
```

### 2. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 API Reference

### Document Management

```bash
# Upload file
POST /v1/documents/ingest/file
Content-Type: multipart/form-data
file: [your-document.pdf]

# Ingest text
POST /v1/documents/ingest
{
  "text": "Document content...",
  "filename": "document.txt"
}
```

### RAG Q&A

```bash
# Ask a question
POST /v1/rag/query
{
  "query": "What are the main contract terms?"
}
```

### Advanced Analysis

```bash
# Synthesize multiple documents
POST /v1/analysis/synthesize
{
  "query": "What are the common themes?"
}

# Compare two documents
POST /v1/analysis/compare
{
  "document1_id": "doc_abc123",
  "document2_id": "doc_xyz789"
}

# Extract insights
POST /v1/analysis/insights
{
  "document_id": "doc_abc123"
}
```

---

## 🧪 Tech Stack

| Layer | Technology | Why? |
|-------|------------|------|
| **Frontend** | React + TypeScript | Type safety, component architecture |
| **Styling** | TailwindCSS + Radix UI | Rapid development, accessible components |
| **State** | Zustand | Simple, performant state management |
| **Backend** | FastAPI | Async, Python, auto-docs |
| **AI** | Google Gemini | Multimodal, cost-effective |
| **Embeddings** | Gemini Embeddings | Consistent with LLM |
| **Vector DB** | Pinecone | Serverless, scalable |
| **Cache** | Redis | Sub-millisecond lookups |
| **Deployment** | Docker | Consistent environments |

---

## 🎨 Design

- **Theme**: Dark mode with RCB-inspired red accents
- **Colors**:
  - Primary: `#D1122D` (RCB Red)
  - Background: `#0a0a0a` (Deep Black)
  - Accents: Gradient effects and glow animations
- **Typography**: Clean, modern sans-serif
- **UX**: Intuitive navigation, real-time feedback

---

## 📁 Project Structure

```
document-analyzer/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API Routes
│   │   │   ├── documents.py    # Document CRUD
│   │   │   ├── rag.py         # RAG Q&A
│   │   │   └── analysis.py    # Synthesis/Compare/Insights
│   │   ├── core/              # Config, Security, Logging
│   │   ├── models/            # Pydantic Schemas
│   │   └── services/          # Business Logic
│   │       ├── document/        # Document processing
│   │       ├── vector/        # Pinecone integration
│   │       ├── embedding/     # Gemini embeddings
│   │       ├── llm/           # Gemini LLM
│   │       └── cache/         # Redis caching
│   └── requirements.txt
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page views
│   │   │   ├── Dashboard.tsx  # Home with stats
│   │   │   ├── Documents.tsx   # Upload & manage
│   │   │   ├── Chat.tsx       # RAG Q&A interface
│   │   │   ├── Analysis.tsx   # Advanced features
│   │   │   └── Settings.tsx    # Configuration
│   │   ├── services/          # API client
│   │   ├── store/             # Zustand state
│   │   └── types/             # TypeScript types
│   └── package.json
│
├── docker-compose.yml          # Full stack deployment
└── README.md
```

---

## 💡 Use Cases

### Legal
- Contract review and comparison
- Clause extraction and analysis
- Risk identification

### Business
- Meeting notes summarization
- Action item tracking
- Multi-document synthesis

### Research
- Paper comparison
- Literature review
- Key finding extraction

### Compliance
- Policy comparison
- Gap analysis
- Audit trail generation

---

## 🔒 Security

- API Key authentication
- Rate limiting
- Input validation
- Secure secret management via environment variables

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Document ingestion | ~1-2s per page |
| Semantic search | <100ms |
| RAG response | 2-5s |
| Cache hit | <10ms |

---

## 🏆 Hackathon Highlights

### What Makes Us Different

1. **Production-Ready Architecture**
   - Clean separation of concerns
   - Microservices-ready structure
   - Comprehensive error handling

2. **Advanced AI Capabilities**
   - RAG with citation tracking
   - Multi-document reasoning
   - Real-time streaming responses

3. **Modern Tech Stack**
   - Type-safe end-to-end (TypeScript + Python)
   - Containerized deployment
   - Scalable vector database

4. **User Experience**
   - Beautiful dark theme
   - Real-time feedback
   - Intuitive navigation

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Google** for Gemini AI and embeddings
- **Pinecone** for vector database infrastructure
- **FastAPI** for the amazing Python framework
- **React** for the frontend library

---

<div align="center">
  <strong>Built with ❤️ for the GUVI Hackathon</strong>
  <br>
  <sub>DocuLens AI - Your Intelligent Document Companion</sub>
</div>
