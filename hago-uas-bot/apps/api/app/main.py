"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_middleware
from app.database import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(debug=settings.DEBUG)
    import structlog
    log = structlog.get_logger(__name__)
    log.info("startup", app=settings.APP_NAME, version=settings.APP_VERSION, env=settings.ENVIRONMENT)
    yield
    await dispose_engine()
    log.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-powered technical support platform for UAV/UAS engineers, "
            "operators, and developers. Built by Hago Drone Consulting Services."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    register_middleware(app)
    register_exception_handlers(app)

    app.include_router(api_router)

    return app


app = create_app()
