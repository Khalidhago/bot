import math

import pytest

from uav_telemetry import converters


def test_global_position_scaling():
    # Zurich test values in MAVLink integer encoding
    pos = converters.global_position_from_int(
        lat_degE7=473977420, lon_degE7=85455940,
        alt_mm=518000, relative_alt_mm=30000)
    assert pos.latitude == pytest.approx(47.397742)
    assert pos.longitude == pytest.approx(8.545594)
    assert pos.altitude_msl == pytest.approx(518.0)
    assert pos.altitude_rel == pytest.approx(30.0)


def test_battery_scaling():
    batt = converters.battery_from_sys_status(
        voltage_battery_mv=16800, current_battery_ca=1250,
        battery_remaining_pct=87)
    assert batt.voltage == pytest.approx(16.8)
    assert batt.current == pytest.approx(12.5)
    assert batt.remaining == pytest.approx(0.87)


def test_battery_unmeasured_sentinels_become_nan():
    batt = converters.battery_from_sys_status(
        voltage_battery_mv=16800, current_battery_ca=-1,
        battery_remaining_pct=-1)
    assert math.isnan(batt.current)
    assert math.isnan(batt.remaining)


def test_quaternion_identity():
    assert converters.quaternion_from_euler(0, 0, 0) == pytest.approx((0, 0, 0, 1))


def test_quaternion_yaw_90deg():
    x, y, z, w = converters.quaternion_from_euler(0, 0, math.pi / 2)
    assert (x, y) == pytest.approx((0, 0))
    assert z == pytest.approx(math.sin(math.pi / 4))
    assert w == pytest.approx(math.cos(math.pi / 4))


def test_quaternion_is_unit_length():
    for angles in [(0.3, -0.2, 1.0), (1.5, 0.7, -2.9), (-0.1, 1.2, 0.4)]:
        q = converters.quaternion_from_euler(*angles)
        assert math.hypot(*q) == pytest.approx(1.0)


def test_armed_flag():
    assert converters.is_armed(128)
    assert converters.is_armed(128 | 64 | 16)
    assert not converters.is_armed(0)
    assert not converters.is_armed(64 | 16)


def test_gps_fix_threshold():
    assert not converters.gps_fix_ok(0)   # no GPS
    assert not converters.gps_fix_ok(2)   # 2D
    assert converters.gps_fix_ok(3)       # 3D
    assert converters.gps_fix_ok(6)       # RTK fixed
