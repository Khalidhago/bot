"""Flight log upload and analysis endpoints."""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError
from app.database import get_session
from app.log_analysis.report_generator import analyze_log
from app.models.flight_log import FlightLog
from app.models.user import User
from app.schemas.flight_log import FlightLogResponse, FlightLogUploadResponse
from app.security.input_validator import validate_filename

router = APIRouter(tags=["flight-logs"])

_LOG_TYPE_MAP = {
    ".ulg": "ulog",
    ".ulog": "ulog",
    ".bin": "dataflash",
    ".log": "dataflash",
    ".csv": "csv",
    ".json": "json",
}


def _detect_log_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _LOG_TYPE_MAP.get(ext, "unknown")


@router.post("/flight-logs/upload", response_model=FlightLogUploadResponse, status_code=201)
async def upload_flight_log(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FlightLogUploadResponse:
    settings = get_settings()
    safe_name = validate_filename(file.filename or "log.bin")
    content = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise DocumentProcessingError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    log_type = _detect_log_type(safe_name)
    log_id = uuid.uuid4()

    upload_path = os.path.join(settings.UPLOAD_DIR, str(user.id), "logs", str(log_id))
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    log = FlightLog(
        id=log_id,
        user_id=user.id,
        filename=safe_name,
        file_path=file_path,
        log_type=log_type,
        status="pending",
    )
    session.add(log)
    await session.flush()
    return FlightLogUploadResponse.model_validate(log)


@router.post("/flight-logs/{log_id}/analyze", response_model=FlightLogResponse)
async def analyze_flight_log(
    log_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FlightLogResponse:
    from sqlalchemy import select

    result = await session.execute(
        select(FlightLog).where(FlightLog.id == log_id, FlightLog.user_id == user.id)
    )
    log = result.scalar_one_or_none()
    if log is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Flight log not found.")

    from datetime import UTC, datetime

    log.status = "processing"
    await session.flush()

    try:
        with open(log.file_path, "rb") as f:
            content = f.read()

        analysis = analyze_log(log.id, log.filename, log.log_type, content)
        log.analysis_result = analysis.model_dump(mode="json")
        log.status = "ready"
        log.analyzed_at = datetime.now(UTC)
    except Exception as exc:
        log.status = "failed"
        log.analysis_result = {"error": str(exc)}

    await session.flush()
    return FlightLogResponse.model_validate(log)


@router.get("/flight-logs", response_model=list[FlightLogResponse])
async def list_flight_logs(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[FlightLogResponse]:
    from sqlalchemy import select

    result = await session.execute(
        select(FlightLog)
        .where(FlightLog.user_id == user.id)
        .order_by(FlightLog.created_at.desc())
    )
    logs = result.scalars().all()
    return [FlightLogResponse.model_validate(log) for log in logs]
