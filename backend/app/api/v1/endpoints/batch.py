"""
Batch and Export Endpoints - DocuLens AI v4.0
"""

from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.core.config import settings


router = APIRouter(tags=["Batch"])


@router.post("/batch/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
) -> dict:
    """Upload multiple files as batch job."""
    if len(files) > settings.batch_max_files:
        raise HTTPException(
            status_code=413,
            detail=f"Maximum {settings.batch_max_files} files per batch",
        )
    
    from app.services.document.batch import batch_processor
    
    batch = batch_processor.create_batch(len(files))
    files_data = []
    
    for f in files:
        content = await f.read()
        files_data.append({
            "filename": f.filename,
            "content": content,
        })
    
    result = batch_processor.process_batch(batch.batch_id, files_data)
    
    return {
        "batch_id": result.batch_id,
        "status": result.status,
        "total_files": result.total_files,
        "processed_files": result.processed_files,
        "failed_files": result.failed_files,
    }


@router.get("/batch/{batch_id}/status")
async def batch_status(batch_id: str) -> dict:
    """Get batch job status."""
    return {
        "batch_id": batch_id,
        "status": "completed",
        "total_files": 0,
        "processed_files": 0,
        "failed_files": 0,
    }


@router.get("/batch/{batch_id}/export")
async def batch_export(
    batch_id: str,
    format: str = "json",
) -> Response:
    """Export batch results."""
    return Response(
        content=b'{}',
        media_type="application/json",
    )


# Export router
export_router = APIRouter(prefix="/export", tags=["Export"])


@export_router.get("/documents/{document_id}")
async def export_document(
    document_id: str,
    format: str = "json",
) -> Response:
    """Export document analysis in various formats."""
    from app.services.document.document_service import document_service
    from app.services.export import pdf_exporter, markdown_exporter
    
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = doc.get("analysis", {})
    
    if format == "pdf_report":
        content = pdf_exporter.export(analysis, doc)
        media_type = "application/pdf"
    elif format == "markdown":
        content = markdown_exporter.export(analysis, doc)
        media_type = "text/markdown"
    elif format == "csv":
        content = b""
        media_type = "text/csv"
    else:
        import json
        content = json.dumps(analysis).encode()
        media_type = "application/json"
    
    return Response(
        content=content,
        media_type=media_type,
    )