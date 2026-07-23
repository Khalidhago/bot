"""Chat request and response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32_000)
    conversation_id: uuid.UUID | None = None
    mode: str = "general"


class SourceReference(BaseModel):
    document_id: uuid.UUID | None = None
    title: str
    chunk_index: int | None = None
    relevance_score: float | None = None
    source_type: str = "knowledge_base"


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    content: str
    role: str = "assistant"
    sources: list[SourceReference] = []
    model_used: str | None = None
    tokens_used: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: uuid.UUID
    title: str
    mode: str
    message_count: int = 0
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    sources: list[SourceReference] | None = None
    tokens_used: int | None = None
    model_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: uuid.UUID
    title: str
    mode: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StreamChunk(BaseModel):
    """A single chunk in a streaming response."""

    type: str  # "token" | "sources" | "done" | "error"
    data: Any = None
    conversation_id: uuid.UUID | None = None
    message_id: uuid.UUID | None = None
