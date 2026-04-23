"""
Upload Endpoints - DocuLens AI v4.0
Upload with auto-analysis trigger
"""

import io
import time
import uuid
from typing import List, Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.schemas import (
    UploadRequest,
    UploadResponse,
    UploadStreamResponse,
)


router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_FILE_SIZE = settings.max_file_size_bytes


def read_image_from_file(file: UploadFile) -> np.ndarray:
    """Convert uploaded file to OpenCV image."""
    from PIL import Image
    
    contents = file.file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    image = Image.open(io.BytesIO(contents))
    
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    return np.array(image)


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    auto_analyze: bool = True,
) -> UploadResponse:
    """
    Upload file with automatic analysis trigger.
    
    - Triggers auto-analysis on upload
    - Ingests to RAG system
    - Returns full analysis results
    """
    start_time = time.time()
    
    # Process file
    from app.services.processing.file_processor import FileProcessor
    processor = FileProcessor()
    
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    result = processor.process_file(contents)
    
    if result.status == "failed":
        raise HTTPException(status_code=400, detail=result.error)
    
    document_id = result.metadata.get("document_id", f"doc_{uuid.uuid4().hex[:12]}")
    
    # Trigger auto-analysis
    analysis_result = None
    if auto_analyze:
        from app.services.analysis.auto_analysis import auto_analysis_service
        analysis_result = auto_analysis_service.analyze(
            document_id, result.text
        )
    
    # Ingest to RAG
    if result.text:
        from app.services.document.document_service import document_service
        try:
            document_service.ingest_to_vector(
                document_id=document_id,
                content=result.text,
                metadata=result.metadata.to_dict() if hasattr(result.metadata, 'to_dict') else {},
            )
        except Exception:
            pass  # RAG ingestion is best-effort
    
    # Dispatch webhook if enabled
    try:
        from app.services.webhook.dispatcher import webhook_dispatcher
        webhook_dispatcher.dispatch("document.ready", {
            "document_id": document_id,
            "filename": file.filename,
            "status": "ready",
        })
    except Exception:
        pass
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        file_type=result.metadata.get("file_type", "unknown"),
        status="success",
        processing_status="completed" if analysis_result else "pending",
        analysis=analysis_result.__dict__ if analysis_result else None,
        processing_time_ms=processing_time_ms,
    )


@router.post("/stream")
async def upload_file_stream(
    file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Upload with SSE streaming of analysis stages.
    
    Streams progress as each stage completes.
    """
    from fastapi import FastAPI
    import sse_starlette as sse
    
    async def event_generator():
        start_time = time.time()
        
        # Stage 1: File validation
        yield sse.MessageEvent(data="""{"step": "validating", "progress": 10}""")
        
        # Process file
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            yield sse.MessageEvent(data="""{"step": "error", "message": "File too large"}""")
            return
        
        yield sse.MessageEvent(data="""{"step": "processing", "progress": 30}""")
        
        # Stage 2: Analysis
        from app.services.analysis.auto_analysis import auto_analysis_service
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        yield sse.MessageEvent(data=f"""{{"step": "analyzing", "progress": 50, "document_id": "{document_id}"}}""")
        
        # Run analysis
        from app.services.processing.file_processor import FileProcessor
        processor = FileProcessor()
        file_result = processor.process_file(contents)
        
        if file_result.status == "success":
            analysis = auto_analysis_service.analyze(document_id, file_result.text)
            yield sse.MessageEvent(data=f"""{{"step": "analyzing", "progress": 70, "status": "{analysis.status}"}}""")
        
        # Stage 3: Complete
        processing_time_ms = int((time.time() - start_time) * 1000)
        yield sse.MessageEvent(data=f"""{{"step": "completed", "progress": 100, "processing_time_ms": {processing_time_ms}}}""")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )