"""Document upload and knowledge search endpoints."""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError
from app.database import get_session
from app.models.document import Document
from app.models.user import User
from app.rag.document_ingestion import ingest_document
from app.rag.embeddings import generate_embeddings
from app.rag.retriever import retrieve, format_rag_context
from app.repositories.base import BaseRepository
from app.schemas.document import (
    DocumentResponse,
    DocumentUploadResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from app.security.input_validator import validate_filename

router = APIRouter(tags=["documents"])


@router.post("/documents/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentUploadResponse:
    settings = get_settings()

    safe_name = validate_filename(file.filename or "upload.bin")
    content = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise DocumentProcessingError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    mime_type, chunks = ingest_document(safe_name, content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

    # Persist document record
    doc_id = uuid.uuid4()
    upload_path = os.path.join(settings.UPLOAD_DIR, str(user.id), str(doc_id))
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=safe_name,
        file_path=file_path,
        mime_type=mime_type,
        status="processing",
        chunk_count=len(chunks),
    )
    session.add(doc)
    await session.flush()

    # Generate embeddings and persist chunks
    try:
        texts = [c.content for c in chunks]
        embeddings = await generate_embeddings(texts)

        from datetime import UTC, datetime
        from app.models.document import DocumentChunk

        for chunk, embedding in zip(chunks, embeddings):
            db_chunk = DocumentChunk(
                document_id=doc_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                chunk_metadata={**chunk.metadata, "embedding": embedding},
            )
            session.add(db_chunk)

        doc.status = "ready"
        doc.ingested_at = datetime.now(UTC)

    except Exception:
        doc.status = "failed"

    await session.flush()
    return DocumentUploadResponse.model_validate(doc)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[DocumentResponse]:
    from sqlalchemy import select

    result = await session.execute(
        select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("/knowledge/search", response_model=list[KnowledgeSearchResult])
async def knowledge_search(
    request: KnowledgeSearchRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[KnowledgeSearchResult]:
    chunks = await retrieve(session, request.query, top_k=request.top_k, document_ids=request.document_ids)
    return [
        KnowledgeSearchResult(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            document_filename=c.document_filename,
            content=c.content,
            relevance_score=c.relevance_score,
            chunk_index=c.chunk_index,
        )
        for c in chunks
    ]
