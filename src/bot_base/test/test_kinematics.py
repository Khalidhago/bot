import math

import pytest

from bot_base.kinematics import DiffDriveKinematics, Odometry, clamp
from bot_base.motor_driver import MockMotorDriver

WHEEL_RADIUS = 0.045
WHEEL_SEPARATION = 0.26


@pytest.fixture
def kin():
    return DiffDriveKinematics(WHEEL_RADIUS, WHEEL_SEPARATION)


def test_clamp():
    assert clamp(5.0, 1.0) == 1.0
    assert clamp(-5.0, 1.0) == -1.0
    assert clamp(0.3, 1.0) == 0.3


def test_straight_line_wheel_speeds(kin):
    left, right = kin.to_wheel_speeds(0.45, 0.0)
    assert left == pytest.approx(right)
    assert left == pytest.approx(0.45 / WHEEL_RADIUS)


def test_turn_in_place_wheel_speeds(kin):
    left, right = kin.to_wheel_speeds(0.0, 1.0)
    assert left == pytest.approx(-right)
    assert right == pytest.approx(WHEEL_SEPARATION / 2 / WHEEL_RADIUS)


def test_inverse_forward_roundtrip(kin):
    for linear, angular in [(0.3, 0.5), (-0.2, 1.2), (0.0, -2.0), (0.5, 0.0)]:
        left, right = kin.to_wheel_speeds(linear, angular)
        assert kin.to_body_twist(left, right) == pytest.approx((linear, angular))


def test_wheel_speed_limit_preserves_curvature():
    kin = DiffDriveKinematics(WHEEL_RADIUS, WHEEL_SEPARATION, max_wheel_speed=5.0)
    left, right = kin.to_wheel_speeds(2.0, 3.0)  # far beyond the limit
    assert max(abs(left), abs(right)) == pytest.approx(5.0)
    # Curvature (ratio of wheel speeds) must be unchanged by the scaling.
    unlimited = DiffDriveKinematics(WHEEL_RADIUS, WHEEL_SEPARATION)
    ul, ur = unlimited.to_wheel_speeds(2.0, 3.0)
    assert left / right == pytest.approx(ul / ur)


def test_odometry_straight_line(kin):
    odom = Odometry(kin)
    wheel_speed = 1.0 / WHEEL_RADIUS  # 1 m/s
    for _ in range(100):
        odom.update(wheel_speed, wheel_speed, 0.01)
    assert odom.x == pytest.approx(1.0)
    assert odom.y == pytest.approx(0.0)
    assert odom.heading == pytest.approx(0.0)


def test_odometry_turn_in_place(kin):
    odom = Odometry(kin)
    left, right = kin.to_wheel_speeds(0.0, math.pi / 2)
    for _ in range(100):
        odom.update(left, right, 0.01)
    assert odom.x == pytest.approx(0.0, abs=1e-9)
    assert odom.y == pytest.approx(0.0, abs=1e-9)
    assert odom.heading == pytest.approx(math.pi / 2)


def test_odometry_quarter_circle_arc(kin):
    """Driving a constant-curvature arc through 90 degrees must land on the
    analytically known end pose (radius, radius, pi/2)."""
    odom = Odometry(kin)
    radius = 0.5
    angular = 1.0
    left, right = kin.to_wheel_speeds(radius * angular, angular)
    steps = 1000
    total_time = (math.pi / 2) / angular
    for _ in range(steps):
        odom.update(left, right, total_time / steps)
    assert odom.x == pytest.approx(radius, rel=1e-6)
    assert odom.y == pytest.approx(radius, rel=1e-6)
    assert odom.heading == pytest.approx(math.pi / 2)


def test_odometry_heading_wraps(kin):
    odom = Odometry(kin)
    left, right = kin.to_wheel_speeds(0.0, 1.0)
    for _ in range(1000):  # 10 s at 1 rad/s -> beyond pi
        odom.update(left, right, 0.01)
    assert -math.pi <= odom.heading <= math.pi


def test_odometry_ignores_nonpositive_dt(kin):
    odom = Odometry(kin)
    odom.update(1.0, 1.0, 0.0)
    odom.update(1.0, 1.0, -0.5)
    assert (odom.x, odom.y, odom.heading) == (0.0, 0.0, 0.0)


def test_mock_driver_converges_to_setpoint():
    driver = MockMotorDriver(time_constant=0.1)
    driver.set_wheel_speeds(2.0, -1.0)
    for _ in range(100):
        driver.advance(0.05)
    left, right = driver.get_wheel_speeds()
    assert left == pytest.approx(2.0, abs=1e-3)
    assert right == pytest.approx(-1.0, abs=1e-3)


def test_mock_driver_stop():
    driver = MockMotorDriver(time_constant=0.05)
    driver.set_wheel_speeds(3.0, 3.0)
    driver.advance(1.0)
    driver.stop()
    driver.advance(1.0)
    assert driver.get_wheel_speeds() == pytest.approx((0.0, 0.0))
