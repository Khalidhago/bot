"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    service = AuthService(session)
    user = await service.register(request)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    service = AuthService(session)
    return await service.login(request.email, request.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    service = AuthService(session)
    return await service.refresh(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    token = authorization.removeprefix("Bearer ").strip()
    service = AuthService(session)
    user = await service.get_current_user(token)
    return UserResponse.model_validate(user)
