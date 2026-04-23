"""Batch Processing Background Task - Celery"""

import uuid
from typing import List

from celery import Task
from celery.result import AsyncResult

from app.worker import celery_app


@celery_app.task(bind=True, name="app.worker.tasks.batch.process_batch")
def process_batch(
    self: Task, batch_id: str, file_paths: List[str]
) -> AsyncResult:
    """Process multiple documents in a batch."""
    from app.worker.tasks.analyze import run_analysis

    results = []
    total = len(file_paths)

    for i, file_path in enumerate(file_paths):
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total,
                "file": file_path.split("/")[-1],
            },
        )

        result = run_analysis.apply_async(args=[document_id, file_path])
        result_wait = result.get(timeout=300)

        results.append(
            {
                "document_id": document_id,
                "status": result_wait.get("status"),
                "error": result_wait.get("error"),
            }
        )

    return {
        "batch_id": batch_id,
        "status": "completed",
        "total": total,
        "results": results,
    }


@celery_app.task(bind=True, name="app.worker.tasks.batch.upload_batch")
def upload_batch(
    self: Task, batch_id: str, files_data: List[dict]
) -> AsyncResult:
    """Upload and process multiple files as a batch."""
    results = []
    total = len(files_data)
    processed = 0
    failed = 0

    for i, file_data in enumerate(files_data):
        try:
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": total,
                    "file": file_data.get("filename", "unknown"),
                },
            )

            from app.services.processing.file_processor import FileProcessor

            processor = FileProcessor()
            result = processor.process_file(file_data.get("path"))

            if result.status == "success":
                processed += 1
            else:
                failed += 1

            results.append(
                {
                    "filename": file_data.get("filename"),
                    "status": result.status,
                    "error": result.error,
                }
            )

        except Exception as e:
            failed += 1
            results.append(
                {
                    "filename": file_data.get("filename"),
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {
        "batch_id": batch_id,
        "status": "completed",
        "total_files": total,
        "processed": processed,
        "failed": failed,
        "results": results,
    }