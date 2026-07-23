"""Chat service — orchestrates conversations, RAG, and AI responses."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.conversation_engine import ConversationEngine
from app.agents.providers.base_provider import ChatMessage
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.chat import ConversationDetail, ConversationSummary

logger = get_logger(__name__)


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        engine: ConversationEngine | None = None,
    ) -> None:
        self._repo = ConversationRepository(session)
        self._engine = engine or ConversationEngine()

    async def get_or_create_conversation(
        self,
        user: User,
        conversation_id: uuid.UUID | None,
        mode: str,
    ):
        if conversation_id:
            conv = await self._repo.get(conversation_id)
            if conv is None:
                raise NotFoundError("Conversation not found.")
            if conv.user_id != user.id:
                raise ForbiddenError()
            return conv
        return await self._repo.create(user_id=user.id, mode=mode)

    async def list_conversations(self, user: User) -> list[ConversationSummary]:
        conversations = await self._repo.list_for_user(user.id)
        summaries = []
        for conv in conversations:
            msg_count = len(conv.messages) if hasattr(conv, "messages") and conv.messages else 0
            summaries.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    mode=conv.mode,
                    message_count=msg_count,
                    updated_at=conv.updated_at,
                )
            )
        return summaries

    async def get_conversation(
        self, user: User, conversation_id: uuid.UUID
    ) -> ConversationDetail:
        conv = await self._repo.get_with_messages(conversation_id)
        if conv is None:
            raise NotFoundError("Conversation not found.")
        if conv.user_id != user.id:
            raise ForbiddenError()
        return ConversationDetail.model_validate(conv)

    async def send_message(
        self,
        user: User,
        user_message: str,
        conversation_id: uuid.UUID | None,
        mode: str,
        rag_context: str | None = None,
    ) -> tuple[uuid.UUID, str, str, int]:
        """Return (conversation_id, response_text, model_name, tokens)."""
        conv = await self.get_or_create_conversation(user, conversation_id, mode)

        # Persist user message
        await self._repo.add_message(conv.id, role="user", content=user_message)

        # Build history
        full_conv = await self._repo.get_with_messages(conv.id)
        history = [
            ChatMessage(role=m.role, content=m.content)
            for m in (full_conv.messages if full_conv else [])
            if m.role != "user" or m.content != user_message
        ]

        content, model, tokens = await self._engine.complete(
            user_message=user_message,
            mode=mode,
            history=history,
            rag_context=rag_context,
        )

        # Auto-title on first exchange
        if conv.title == "New Conversation":
            title = user_message[:80] + "…" if len(user_message) > 80 else user_message
            conv.title = title

        await self._repo.add_message(
            conv.id,
            role="assistant",
            content=content,
            tokens_used=tokens,
            model_used=model,
        )

        logger.info("chat_complete", conversation_id=str(conv.id), model=model, tokens=tokens)
        return conv.id, content, model, tokens

    async def stream_message(
        self,
        user: User,
        user_message: str,
        conversation_id: uuid.UUID | None,
        mode: str,
        rag_context: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield tokens; persist the full message after streaming."""
        conv = await self.get_or_create_conversation(user, conversation_id, mode)
        await self._repo.add_message(conv.id, role="user", content=user_message)

        full_conv = await self._repo.get_with_messages(conv.id)
        history = [
            ChatMessage(role=m.role, content=m.content)
            for m in (full_conv.messages if full_conv else [])
            if m.role != "user" or m.content != user_message
        ]

        collected: list[str] = []
        model_used = ""
        task = self._engine._router.classify_task(user_message)
        provider, model_used = self._engine._router.get_provider(task)
        messages = self._engine._build_messages(user_message, mode, history, rag_context)

        async for token in provider.stream(messages, model=model_used):
            collected.append(token)
            yield token

        full_response = "".join(collected)
        await self._repo.add_message(
            conv.id,
            role="assistant",
            content=full_response,
            model_used=model_used,
        )
