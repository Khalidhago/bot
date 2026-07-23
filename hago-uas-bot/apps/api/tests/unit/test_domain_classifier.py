"""Tests for UAV domain classifier."""

from __future__ import annotations

from app.uav.domain_classifier import classify_domain


class TestDomainClassifier:
    def test_px4_detected(self) -> None:
        result = classify_domain("How do I tune EKF2_AID_MASK in PX4?")
        assert result.domain == "px4"
        assert result.confidence > 0

    def test_ardupilot_detected(self) -> None:
        result = classify_domain("How do I analyze ArduCopter DataFlash logs?")
        assert result.domain == "ardupilot"

    def test_ros2_detected(self) -> None:
        result = classify_domain("How do I create a ROS 2 node with rclpy?")
        assert result.domain == "ros2"

    def test_ai_ml_detected(self) -> None:
        result = classify_domain("How do I deploy a YOLO model on NVIDIA Jetson?")
        assert result.domain == "ai_ml"

    def test_general_fallback(self) -> None:
        result = classify_domain("What is a drone?")
        assert result.domain == "general"
        assert result.confidence == 1.0
        assert result.detected_keywords == []
