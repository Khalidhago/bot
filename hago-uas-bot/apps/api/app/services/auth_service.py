"""Authentication service."""

from __future__ import annotations

import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, request: RegisterRequest) -> User:
        existing = await self._repo.get_by_email(request.email)
        if existing:
            raise ConflictError("A user with this email already exists.")
        return await self._repo.create(
            email=request.email.lower(),
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role="engineer",
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("This account has been deactivated.")
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type.")
        user = await self._repo.get(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive.")
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type.")
        user = await self._repo.get(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive.")
        return user
