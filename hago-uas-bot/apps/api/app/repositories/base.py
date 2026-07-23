"""Base repository with common CRUD helpers."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def list(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> list[ModelT]:
        stmt = select(self.model)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self.model, attr) == value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: uuid.UUID) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False
        await self.session.delete(obj)
        return True
