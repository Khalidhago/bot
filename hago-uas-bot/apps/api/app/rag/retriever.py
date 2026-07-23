"""Semantic retrieval from the vector store."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.rag.embeddings import generate_embeddings

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_filename: str
    content: str
    relevance_score: float
    chunk_index: int


async def retrieve(
    session: AsyncSession,
    query: str,
    top_k: int | None = None,
    document_ids: list[uuid.UUID] | None = None,
) -> list[RetrievedChunk]:
    """Return the top-k most relevant chunks for a query."""
    settings = get_settings()
    k = top_k or settings.RAG_TOP_K

    query_embeddings = await generate_embeddings([query])
    query_vector = query_embeddings[0]

    # pgvector cosine similarity — requires the vector column
    vector_literal = f"[{','.join(str(v) for v in query_vector)}]"

    doc_filter = ""
    if document_ids:
        ids_str = ",".join(f"'{str(d)}'" for d in document_ids)
        doc_filter = f"AND dc.document_id IN ({ids_str})"

    sql = text(
        f"""
        SELECT
            dc.id AS chunk_id,
            dc.document_id,
            d.filename AS document_filename,
            dc.content,
            dc.chunk_index,
            1 - (dc.embedding <=> :query_vector::vector) AS score
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE d.status = 'ready'
        {doc_filter}
        ORDER BY dc.embedding <=> :query_vector::vector
        LIMIT :top_k
        """
    )

    try:
        result = await session.execute(
            sql, {"query_vector": vector_literal, "top_k": k}
        )
        rows = result.fetchall()
        return [
            RetrievedChunk(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                document_filename=row.document_filename,
                content=row.content,
                relevance_score=float(row.score),
                chunk_index=row.chunk_index,
            )
            for row in rows
        ]
    except Exception as exc:
        logger.warning("retrieval_failed", error=str(exc))
        return []


def format_rag_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    if not chunks:
        return ""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[{i}] Source: {chunk.document_filename} (chunk {chunk.chunk_index}, "
            f"score: {chunk.relevance_score:.2f})\n{chunk.content}"
        )
    return "\n\n---\n\n".join(parts)
