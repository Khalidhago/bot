"""Tests for anomaly detector."""

from __future__ import annotations

from app.log_analysis.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    def setup_method(self) -> None:
        self.detector = AnomalyDetector()

    def test_no_anomalies_on_clean_data(self) -> None:
        telemetry = {
            "gps": {"fix_type": 3, "hdop": 1.2},
            "battery": {"voltage_min_v": 22.2, "cell_count": 6},
            "vibration": {"vibe_x_rms": 5.0, "vibe_y_rms": 4.5, "vibe_z_rms": 6.0},
            "ekf": {"innovation_flags": 0},
            "motors": {"max_outputs": [60, 62, 58, 61]},
        }
        findings = self.detector.detect(telemetry)
        assert findings == []

    def test_gps_fix_below_3d(self) -> None:
        telemetry = {"gps": {"fix_type": 2, "hdop": 1.0}}
        findings = self.detector.detect(telemetry)
        categories = [f.category for f in findings]
        assert "GPS" in categories

    def test_high_hdop(self) -> None:
        telemetry = {"gps": {"fix_type": 3, "hdop": 3.5}}
        findings = self.detector.detect(telemetry)
        assert any(f.category == "GPS" for f in findings)

    def test_low_battery_cell_voltage(self) -> None:
        telemetry = {"battery": {"voltage_min_v": 18.0, "cell_count": 6}}  # 3.0V/cell
        findings = self.detector.detect(telemetry)
        assert any(f.category == "Battery" for f in findings)
        batt = next(f for f in findings if f.category == "Battery")
        assert batt.severity == "critical"

    def test_high_vibration(self) -> None:
        telemetry = {"vibration": {"vibe_z_rms": 75.0}}
        findings = self.detector.detect(telemetry)
        assert any(f.category == "Vibration" for f in findings)

    def test_ekf_flags(self) -> None:
        telemetry = {"ekf": {"innovation_flags": 0b00000100}}
        findings = self.detector.detect(telemetry)
        assert any(f.category == "EKF" for f in findings)

    def test_motor_saturation(self) -> None:
        telemetry = {"motors": {"max_outputs": [97.5, 60, 61, 58]}}
        findings = self.detector.detect(telemetry)
        assert any(f.category == "Motor" for f in findings)

    def test_empty_telemetry_no_crash(self) -> None:
        findings = self.detector.detect({})
        assert isinstance(findings, list)
