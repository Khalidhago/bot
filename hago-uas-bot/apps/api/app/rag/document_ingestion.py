"""Document ingestion pipeline: extract → chunk → embed → store."""

from __future__ import annotations

import io
import mimetypes
from pathlib import Path

from app.core.exceptions import DocumentProcessingError
from app.core.logging import get_logger
from app.rag.chunking import Chunk, chunk_text

logger = get_logger(__name__)

SUPPORTED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def detect_mime_type(filename: str, content: bytes) -> str:
    guessed, _ = mimetypes.guess_type(filename)
    if guessed:
        return guessed
    if content[:4] == b"%PDF":
        return "application/pdf"
    try:
        content.decode("utf-8")
        return "text/plain"
    except UnicodeDecodeError:
        return "application/octet-stream"


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        pages: list[str] = []
        for page in doc:
            pages.append(page.get_text())
        return "\n\n".join(pages)
    except Exception as exc:
        raise DocumentProcessingError(f"PDF extraction failed: {exc}") from exc


def extract_text_from_docx(content: bytes) -> str:
    try:
        from docx import Document as DocxDocument

        doc = DocxDocument(io.BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as exc:
        raise DocumentProcessingError(f"DOCX extraction failed: {exc}") from exc


def extract_text(filename: str, content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return extract_text_from_pdf(content)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(content)
    if mime_type in ("text/plain", "text/markdown"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError("Text file is not valid UTF-8.") from exc
    raise DocumentProcessingError(f"Unsupported MIME type: {mime_type}")


def ingest_document(
    filename: str,
    content: bytes,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> tuple[str, list[Chunk]]:
    """Extract text and split into chunks. Returns (mime_type, chunks)."""
    mime_type = detect_mime_type(filename, content)
    if mime_type not in SUPPORTED_TYPES:
        raise DocumentProcessingError(
            f"File type '{mime_type}' is not supported. "
            f"Supported: PDF, DOCX, TXT, Markdown."
        )

    logger.info("ingesting_document", filename=filename, mime_type=mime_type)
    text = extract_text(filename, content, mime_type)

    if not text.strip():
        raise DocumentProcessingError("Document appears to be empty after text extraction.")

    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    logger.info("document_chunked", filename=filename, chunks=len(chunks))
    return mime_type, chunks
