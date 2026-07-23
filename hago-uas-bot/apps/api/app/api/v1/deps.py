"""Shared auth dependency for protected endpoints."""

from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.services.auth_service import AuthService


async def get_current_user(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_session),
) -> User:
    token = authorization.removeprefix("Bearer ").strip()
    return await AuthService(session).get_current_user(token)
