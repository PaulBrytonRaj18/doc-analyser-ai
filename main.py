"""
AI-Powered Document Analysis & Extraction API
Main application entry point
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import pathlib

from routers import analyze
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

STATIC_DIR = pathlib.Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Document Analyzer API starting up...")
    logger.info("📌 API Version: 2.0.0")
    yield
    logger.info("🛑 AI Document Analyzer API shutting down...")


app = FastAPI(
    title="AI-Powered Document Analysis & Extraction",
    description=(
        "Intelligent document processing system that extracts, analyses, "
        "and summarises content from PDF, DOCX, and image files using AI."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(analyze.router, prefix="/api/v1", tags=["Document Analysis"])

# Mount static assets (CSS, JS)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["App"], include_in_schema=False)
async def serve_app():
    """Serve the main frontend application."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"error": "Frontend not found"}, status_code=404)


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "document-analyzer", "version": "2.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
