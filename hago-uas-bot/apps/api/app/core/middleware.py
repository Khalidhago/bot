"""Request middleware: request IDs, CORS, and audit logging."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        import structlog

        with structlog.contextvars.bound_contextvars(request_id=request_id):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, and duration."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        import time

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=request.client.host if request.client else "unknown",
        )
        return response


def register_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(AuditLogMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
