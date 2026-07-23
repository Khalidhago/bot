"""Background Celery tasks."""

from __future__ import annotations

from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def ingest_document_task(self, document_id: str) -> dict:
    """Background task: generate embeddings and index a document."""
    try:
        logger.info("ingest_document_task_start", document_id=document_id)
        # Full implementation: load document from DB, generate embeddings,
        # store pgvector rows. Triggered asynchronously after upload.
        return {"status": "ok", "document_id": document_id}
    except Exception as exc:
        logger.error("ingest_document_task_failed", document_id=document_id, error=str(exc))
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc


@celery_app.task(bind=True, max_retries=2)
def analyze_flight_log_task(self, log_id: str) -> dict:
    """Background task: parse and analyze a flight log."""
    try:
        logger.info("analyze_flight_log_task_start", log_id=log_id)
        return {"status": "ok", "log_id": log_id}
    except Exception as exc:
        logger.error("analyze_flight_log_task_failed", log_id=log_id, error=str(exc))
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
