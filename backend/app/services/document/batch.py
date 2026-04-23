"""
Batch Processing Service - DocuLens AI v4.0
Batch document processing with progress tracking
"""

import uuid
import time
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional

from app.core.config import settings


@dataclass
class BatchJobStatus:
    batch_id: str
    status: str
    total_files: int
    processed_files: int
    failed_files: int
    results: List[dict] = field(default_factory=list)
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class BatchProcessor:
    """Process multiple documents in batch."""

    def __init__(self):
        self.max_files = settings.batch_max_files

    def create_batch(
        self,
        file_count: int,
        trigger_celery: bool = False,
    ) -> BatchJobStatus:
        """Create a new batch job."""
        if file_count > self.max_files:
            raise ValueError(f"Maximum {self.max_files} files per batch")

        batch_id = f"batch_{hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:12]}"

        return BatchJobStatus(
            batch_id=batch_id,
            status="pending",
            total_files=file_count,
            processed_files=0,
            failed_files=0,
            results=[],
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    def process_batch(
        self,
        batch_id: str,
        files_data: List[dict],
        trigger_celery: bool = False,
    ) -> BatchJobStatus:
        """Process batch of files."""
        if trigger_celery and settings.celery_enabled:
            from app.worker.tasks.batch import upload_batch
            
            upload_batch.apply_async(args=[batch_id, files_data])
            
            return BatchJobStatus(
                batch_id=batch_id,
                status="queued",
                total_files=len(files_data),
                processed_files=0,
                failed_files=0,
                results=[],
                created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            )

        results = []
        processed = 0
        failed = 0

        for i, file_data in enumerate(files_data):
            try:
                from app.services.processing.file_processor import FileProcessor
                processor = FileProcessor()
                result = processor.process_file(file_data.get("path"))
                results.append({
                    "filename": file_data.get("filename"),
                    "status": result.status,
                    "document_id": result.metadata.get("document_id"),
                    "error": result.error,
                })
                if result.status == "success":
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                results.append({
                    "filename": file_data.get("filename"),
                    "status": "failed",
                    "error": str(e),
                })
                failed += 1

        return BatchJobStatus(
            batch_id=batch_id,
            status="completed",
            total_files=len(files_data),
            processed_files=processed,
            failed_files=failed,
            results=results,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            completed_at=time.strftime("%Y-%m-%dT%H:%M:%S") if processed + failed == len(files_data) else None,
        )


batch_processor = BatchProcessor()