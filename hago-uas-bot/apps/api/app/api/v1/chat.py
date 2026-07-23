"""Chat and conversation endpoints (REST + WebSocket streaming)."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database import get_session
from app.models.user import User
from app.rag.retriever import format_rag_context, retrieve
from app.schemas.chat import ChatRequest, ChatResponse, ConversationDetail, ConversationSummary
from app.security.input_validator import sanitize_user_input
from app.services.chat_service import ChatService
from app.core.logging import get_logger

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    safe_message = sanitize_user_input(request.message)

    # RAG retrieval
    chunks = await retrieve(session, safe_message)
    rag_context = format_rag_context(chunks) if chunks else None

    service = ChatService(session)
    conv_id, content, model, tokens = await service.send_message(
        user=user,
        user_message=safe_message,
        conversation_id=request.conversation_id,
        mode=request.mode,
        rag_context=rag_context,
    )

    from app.schemas.chat import SourceReference
    from datetime import datetime, UTC

    sources = [
        SourceReference(
            document_id=c.document_id,
            title=c.document_filename,
            chunk_index=c.chunk_index,
            relevance_score=c.relevance_score,
        )
        for c in chunks
    ]

    return ChatResponse(
        conversation_id=conv_id,
        message_id=uuid.uuid4(),
        content=content,
        sources=sources,
        model_used=model,
        tokens_used=tokens,
        created_at=datetime.now(UTC),
    )


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ConversationSummary]:
    service = ChatService(session)
    return await service.list_conversations(user)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationDetail:
    service = ChatService(session)
    return await service.get_conversation(user, conversation_id)


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> None:
    """WebSocket endpoint for streaming AI responses.

    Protocol:
    - Client sends: {"token": "<jwt>", "message": "...", "mode": "...", "conversation_id": null}
    - Server sends: {"type": "token", "data": "..."}
                    {"type": "sources", "data": [...]}
                    {"type": "done", "conversation_id": "..."}
                    {"type": "error", "data": "..."}
    """
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        payload = json.loads(raw)
    except Exception:
        await websocket.send_text(json.dumps({"type": "error", "data": "Invalid payload."}))
        await websocket.close()
        return

    token = payload.get("token", "")
    message = payload.get("message", "")
    mode = payload.get("mode", "general")
    conversation_id_str = payload.get("conversation_id")
    conversation_id = uuid.UUID(conversation_id_str) if conversation_id_str else None

    try:
        from app.services.auth_service import AuthService
        user = await AuthService(session).get_current_user(token)
        safe_message = sanitize_user_input(message)

        chunks = await retrieve(session, safe_message)
        rag_context = format_rag_context(chunks) if chunks else None

        service = ChatService(session)

        async for token_text in service.stream_message(
            user=user,
            user_message=safe_message,
            conversation_id=conversation_id,
            mode=mode,
            rag_context=rag_context,
        ):
            await websocket.send_text(json.dumps({"type": "token", "data": token_text}))

        if chunks:
            sources_data = [
                {
                    "title": c.document_filename,
                    "chunk_index": c.chunk_index,
                    "relevance_score": c.relevance_score,
                }
                for c in chunks
            ]
            await websocket.send_text(json.dumps({"type": "sources", "data": sources_data}))

        await websocket.send_text(json.dumps({"type": "done"}))

    except WebSocketDisconnect:
        logger.info("ws_chat_disconnected")
    except Exception as exc:
        logger.error("ws_chat_error", error=str(exc))
        try:
            await websocket.send_text(json.dumps({"type": "error", "data": str(exc)}))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
