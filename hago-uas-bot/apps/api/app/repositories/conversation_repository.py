"""Conversation repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_with_messages(self, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        sources: dict | None = None,
        tokens_used: int | None = None,
        model_used: str | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources,
            tokens_used=tokens_used,
            model_used=model_used,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
