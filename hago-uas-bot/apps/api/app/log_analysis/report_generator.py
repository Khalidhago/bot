"""Flight log report generator."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.log_analysis.anomaly_detector import Anomaly, AnomalyDetector
from app.log_analysis.parsers.csv_parser import parse_csv, parse_json_telemetry
from app.schemas.flight_log import AnomalyFinding, FlightLogAnalysisResult

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _anomaly_to_finding(anomaly: Anomaly) -> AnomalyFinding:
    return AnomalyFinding(
        category=anomaly.category,
        problem=anomaly.problem,
        evidence=anomaly.evidence,
        probable_cause=anomaly.probable_cause,
        severity=anomaly.severity,
        confidence=anomaly.confidence,
        recommended_investigation=anomaly.recommended_investigation,
        corrective_action=anomaly.corrective_action,
    )


def _overall_severity(findings: list[AnomalyFinding]) -> str:
    if not findings:
        return "info"
    return min(findings, key=lambda f: _SEVERITY_ORDER.get(f.severity, 99)).severity


def analyze_log(
    log_id: uuid.UUID,
    filename: str,
    log_type: str,
    content: bytes,
) -> FlightLogAnalysisResult:
    """Parse a flight log and return a diagnostic report."""
    if log_type == "csv":
        telemetry = parse_csv(content)
    elif log_type == "json":
        telemetry = parse_json_telemetry(content)
    else:
        # ULog and DataFlash parsers require optional heavy dependencies.
        # Return a structured "unsupported" result instead of crashing.
        return FlightLogAnalysisResult(
            log_id=log_id,
            filename=filename,
            log_type=log_type,
            summary=(
                f"Full parsing for '{log_type}' logs requires the pyulog or pymavlink "
                f"library. Upload a CSV or JSON telemetry export for immediate analysis, "
                f"or ask the AI assistant to interpret your log data."
            ),
            findings=[],
            overall_severity="info",
            analyzed_at=datetime.now(UTC),
        )

    detector = AnomalyDetector()
    anomalies = detector.detect(telemetry)
    findings = [_anomaly_to_finding(a) for a in anomalies]

    summary_parts = [f"Analyzed {log_type.upper()} log: {filename}."]
    if findings:
        categories = {f.category for f in findings}
        summary_parts.append(
            f"Found {len(findings)} issue(s) in: {', '.join(sorted(categories))}."
        )
    else:
        summary_parts.append("No anomalies detected in the parsed telemetry data.")

    return FlightLogAnalysisResult(
        log_id=log_id,
        filename=filename,
        log_type=log_type,
        summary=" ".join(summary_parts),
        findings=findings,
        overall_severity=_overall_severity(findings),
        analyzed_at=datetime.now(UTC),
        raw_stats=telemetry if log_type in ("csv", "json") else None,
    )
