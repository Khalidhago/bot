"""UAV domain classifier — maps user messages to specialist domains."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DomainClassification:
    domain: str
    confidence: float
    detected_keywords: list[str]


_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "px4": [
        "px4", "pixhawk", "qgroundcontrol", "qgc", "uorb", "nuttx",
        "px4io", "mavsdk", "sitl", "hitl", "gazebo", "mc_roll", "ekf2",
    ],
    "ardupilot": [
        "ardupilot", "arducopter", "arduplane", "ardurover", "ardusub",
        "mission planner", "dataflash", "apm", "cube", "ardu",
    ],
    "ros2": [
        "ros2", "ros 2", "rclpy", "rclcpp", "colcon", "topic", "service",
        "action server", "tf2", "nav2", "dds", "fastdds", "cyclone",
        "xrce", "micro-ros", "mavros",
    ],
    "mavlink": [
        "mavlink", "mavsdk", "heartbeat", "command_long", "mission item",
        "param_set", "mavproxy", "dronekit",
    ],
    "ai_ml": [
        "yolo", "pytorch", "tensorflow", "onnx", "tensorrt", "jetson",
        "inference", "object detection", "semantic segmentation",
        "computer vision", "neural network", "model",
    ],
    "flight_log": [
        "ulog", "dataflash", "bin log", "flight log", "telemetry log",
        "log analysis", "crash analysis", "ekf error", "gps failure",
    ],
    "hardware": [
        "esc", "motor", "propeller", "lidar", "camera", "imu",
        "gps module", "pixhawk", "cube orange", "raspberry pi",
        "jetson nano", "can bus", "uart", "spi", "i2c",
    ],
}


def classify_domain(message: str) -> DomainClassification:
    """Return the most likely UAV domain for a message."""
    lower = message.lower()
    scores: dict[str, list[str]] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        matched = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower)]
        if matched:
            scores[domain] = matched

    if not scores:
        return DomainClassification(domain="general", confidence=1.0, detected_keywords=[])

    best = max(scores, key=lambda d: len(scores[d]))
    total_possible = len(_DOMAIN_KEYWORDS[best])
    confidence = min(len(scores[best]) / max(total_possible, 1) + 0.3, 1.0)
    return DomainClassification(
        domain=best, confidence=round(confidence, 2), detected_keywords=scores[best]
    )
