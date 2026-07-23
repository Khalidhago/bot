"""Flight log schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FlightLogUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    log_type: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnomalyFinding(BaseModel):
    category: str
    problem: str
    evidence: str
    probable_cause: str
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    confidence: str  # "confirmed" | "high" | "medium" | "low" | "insufficient_data"
    recommended_investigation: str
    corrective_action: str


class FlightLogAnalysisResult(BaseModel):
    log_id: uuid.UUID
    filename: str
    log_type: str
    summary: str
    flight_duration_s: float | None = None
    findings: list[AnomalyFinding]
    overall_severity: str
    analyzed_at: datetime
    raw_stats: dict[str, Any] | None = None


class FlightLogResponse(BaseModel):
    id: uuid.UUID
    filename: str
    log_type: str
    status: str
    analysis_result: dict[str, Any] | None = None
    created_at: datetime
    analyzed_at: datetime | None = None

    model_config = {"from_attributes": True}
