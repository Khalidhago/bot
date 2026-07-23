"""Anomaly detector for parsed flight log data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Anomaly:
    category: str
    problem: str
    evidence: str
    probable_cause: str
    severity: str  # critical | high | medium | low | info
    confidence: str  # confirmed | high | medium | low | insufficient_data
    recommended_investigation: str
    corrective_action: str


class AnomalyDetector:
    """Rule-based anomaly detection on parsed telemetry data."""

    def detect(self, telemetry: dict[str, Any]) -> list[Anomaly]:
        """Run all detectors and return all findings."""
        findings: list[Anomaly] = []
        findings.extend(self._check_gps(telemetry))
        findings.extend(self._check_battery(telemetry))
        findings.extend(self._check_vibration(telemetry))
        findings.extend(self._check_ekf(telemetry))
        findings.extend(self._check_motors(telemetry))
        return findings

    # ── GPS ──────────────────────────────────────────────────────────────

    def _check_gps(self, t: dict[str, Any]) -> list[Anomaly]:
        findings: list[Anomaly] = []
        gps = t.get("gps", {})

        fix_type = gps.get("fix_type")
        if fix_type is not None and fix_type < 3:
            findings.append(
                Anomaly(
                    category="GPS",
                    problem="GPS fix below 3D",
                    evidence=f"GPS fix type reported as {fix_type} (3D fix requires ≥3)",
                    probable_cause="Insufficient satellite visibility or signal obstruction",
                    severity="high",
                    confidence="confirmed",
                    recommended_investigation=(
                        "Check GPS satellite count, HDOP, and antenna placement. "
                        "Review EKF GPS fusion health."
                    ),
                    corrective_action=(
                        "Ensure clear sky view for GPS antenna. "
                        "Check for RF interference sources. "
                        "Do not arm until 3D fix is acquired."
                    ),
                )
            )

        hdop = gps.get("hdop")
        if hdop is not None and hdop > 2.0:
            severity = "high" if hdop > 3.0 else "medium"
            findings.append(
                Anomaly(
                    category="GPS",
                    problem="High HDOP (poor horizontal accuracy)",
                    evidence=f"HDOP = {hdop:.2f} (recommended < 1.5)",
                    probable_cause="Limited satellite geometry or signal multipath",
                    severity=severity,
                    confidence="confirmed",
                    recommended_investigation=(
                        "Wait for better satellite geometry. "
                        "Inspect GPS antenna for obstruction."
                    ),
                    corrective_action=(
                        "Delay flight until HDOP < 1.5. "
                        "Reposition GPS antenna for better sky view."
                    ),
                )
            )

        return findings

    # ── Battery ──────────────────────────────────────────────────────────

    def _check_battery(self, t: dict[str, Any]) -> list[Anomaly]:
        findings: list[Anomaly] = []
        battery = t.get("battery", {})

        voltage_min = battery.get("voltage_min_v")
        cell_count = battery.get("cell_count", 1)
        if voltage_min is not None and cell_count > 0:
            cell_voltage = voltage_min / cell_count
            if cell_voltage < 3.5:
                severity = "critical" if cell_voltage < 3.2 else "high"
                findings.append(
                    Anomaly(
                        category="Battery",
                        problem="Cell voltage dropped below safe threshold",
                        evidence=(
                            f"Minimum cell voltage: {cell_voltage:.2f}V "
                            f"(threshold: 3.5V, critical: 3.2V)"
                        ),
                        probable_cause=(
                            "Excessive discharge rate or insufficient capacity for the mission"
                        ),
                        severity=severity,
                        confidence="confirmed",
                        recommended_investigation=(
                            "Review battery C-rating vs peak current draw. "
                            "Inspect battery health with cell balancer."
                        ),
                        corrective_action=(
                            "Use higher-capacity or higher-C-rating battery. "
                            "Reduce payload or mission time. "
                            "Check for damaged cells."
                        ),
                    )
                )

        return findings

    # ── Vibration ────────────────────────────────────────────────────────

    def _check_vibration(self, t: dict[str, Any]) -> list[Anomaly]:
        findings: list[Anomaly] = []
        vibe = t.get("vibration", {})

        for axis in ("x", "y", "z"):
            rms = vibe.get(f"vibe_{axis}_rms")
            if rms is not None and rms > 30.0:
                severity = "high" if rms > 60.0 else "medium"
                findings.append(
                    Anomaly(
                        category="Vibration",
                        problem=f"High vibration on {axis.upper()} axis",
                        evidence=f"Vibration RMS {axis.upper()} = {rms:.1f} m/s² (limit: 30 m/s²)",
                        probable_cause=(
                            "Propeller imbalance, loose motor mount, or frame resonance"
                        ),
                        severity=severity,
                        confidence="high",
                        recommended_investigation=(
                            "Balance propellers. Tighten motor mounts. "
                            "Check frame for cracks. Review IMU FFT data."
                        ),
                        corrective_action=(
                            "Balance or replace propellers. "
                            "Add vibration-damping mount for flight controller. "
                            "Check for motor bearing wear."
                        ),
                    )
                )

        return findings

    # ── EKF ──────────────────────────────────────────────────────────────

    def _check_ekf(self, t: dict[str, Any]) -> list[Anomaly]:
        findings: list[Anomaly] = []
        ekf = t.get("ekf", {})

        flags = ekf.get("innovation_flags", 0)
        if isinstance(flags, int) and flags != 0:
            findings.append(
                Anomaly(
                    category="EKF",
                    problem="EKF innovation test failures detected",
                    evidence=f"EKF innovation flags = {flags:#010b}",
                    probable_cause=(
                        "Sensor inconsistency: GPS, magnetometer, or barometer "
                        "data disagreement"
                    ),
                    severity="high",
                    confidence="high",
                    recommended_investigation=(
                        "Review EKF2_AID_MASK and sensor health. "
                        "Check compass calibration and interference. "
                        "Inspect barometer for pressure disturbance."
                    ),
                    corrective_action=(
                        "Re-calibrate compass away from magnetic interference. "
                        "Re-run accelerometer calibration. "
                        "Verify GPS antenna placement."
                    ),
                )
            )

        return findings

    # ── Motors ───────────────────────────────────────────────────────────

    def _check_motors(self, t: dict[str, Any]) -> list[Anomaly]:
        findings: list[Anomaly] = []
        motors = t.get("motors", {})

        max_outputs = motors.get("max_outputs", [])
        for i, output in enumerate(max_outputs):
            if isinstance(output, (int, float)) and output > 95:
                findings.append(
                    Anomaly(
                        category="Motor",
                        problem=f"Motor {i+1} saturating output",
                        evidence=f"Motor {i+1} maximum output = {output:.1f}% (> 95%)",
                        probable_cause=(
                            "Insufficient thrust margin, motor/ESC mismatch, "
                            "or propeller damage"
                        ),
                        severity="high",
                        confidence="medium",
                        recommended_investigation=(
                            "Perform thrust stand measurement. "
                            "Check motor and ESC temperature during flight. "
                            "Review hover throttle percentage."
                        ),
                        corrective_action=(
                            "Reduce payload weight. "
                            "Upgrade motors/propellers. "
                            "Check for propeller damage or wrong rotation direction."
                        ),
                    )
                )

        return findings
