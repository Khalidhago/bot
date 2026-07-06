"""Differential-drive kinematics and odometry integration.

Pure math, no ROS dependencies, so it is unit-testable without a ROS
environment.
"""
import math
from dataclasses import dataclass


def clamp(value: float, limit: float) -> float:
    """Clamp *value* to the symmetric range [-limit, limit]."""
    return max(-limit, min(limit, value))


@dataclass
class DiffDriveKinematics:
    """Kinematic model of a two-wheel differential-drive base.

    wheel_radius:     drive wheel radius in metres
    wheel_separation: distance between the two wheel contact points in metres
    max_wheel_speed:  wheel angular speed limit in rad/s (0 disables limiting)
    """
    wheel_radius: float
    wheel_separation: float
    max_wheel_speed: float = 0.0

    def to_wheel_speeds(self, linear: float, angular: float) -> tuple[float, float]:
        """Convert a body twist to (left, right) wheel angular speeds in rad/s.

        If a wheel speed limit is set and either wheel would exceed it, both
        wheels are scaled by the same factor so the commanded curvature is
        preserved (the robot slows down but keeps its turn shape).
        """
        left = (linear - angular * self.wheel_separation / 2.0) / self.wheel_radius
        right = (linear + angular * self.wheel_separation / 2.0) / self.wheel_radius

        if self.max_wheel_speed > 0.0:
            fastest = max(abs(left), abs(right))
            if fastest > self.max_wheel_speed:
                scale = self.max_wheel_speed / fastest
                left *= scale
                right *= scale
        return left, right

    def to_body_twist(self, left: float, right: float) -> tuple[float, float]:
        """Convert (left, right) wheel angular speeds in rad/s to a body twist
        (linear m/s, angular rad/s)."""
        linear = self.wheel_radius * (left + right) / 2.0
        angular = self.wheel_radius * (right - left) / self.wheel_separation
        return linear, angular


class Odometry:
    """Dead-reckoning pose integrator for a differential-drive base."""

    def __init__(self, kinematics: DiffDriveKinematics):
        self._kin = kinematics
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

    def reset(self) -> None:
        self.x = self.y = self.heading = 0.0
        self.linear_velocity = self.angular_velocity = 0.0

    def update(self, left_speed: float, right_speed: float, dt: float) -> None:
        """Advance the pose estimate by *dt* seconds given measured wheel
        angular speeds in rad/s.

        Uses the exact arc (constant-curvature) integration, falling back to
        straight-line motion when the angular rate is negligible.
        """
        if dt <= 0.0:
            return
        linear, angular = self._kin.to_body_twist(left_speed, right_speed)
        self.linear_velocity = linear
        self.angular_velocity = angular

        if abs(angular) < 1e-9:
            self.x += linear * dt * math.cos(self.heading)
            self.y += linear * dt * math.sin(self.heading)
        else:
            radius = linear / angular
            new_heading = self.heading + angular * dt
            self.x += radius * (math.sin(new_heading) - math.sin(self.heading))
            self.y += -radius * (math.cos(new_heading) - math.cos(self.heading))
            self.heading = math.atan2(math.sin(new_heading), math.cos(new_heading))
