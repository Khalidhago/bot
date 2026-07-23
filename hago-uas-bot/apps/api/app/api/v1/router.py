"""Main API v1 router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, chat, documents, flight_logs, health

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(chat.router)
router.include_router(documents.router)
router.include_router(flight_logs.router)
