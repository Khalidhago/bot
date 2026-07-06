"""Pure conversion helpers: raw MAVLink message fields -> ROS-friendly values.

MAVLink encodes telemetry in scaled integers (degE7 for coordinates,
millivolts, centiamps, ...). Everything here is unit conversion and framing —
no pymavlink or ROS imports — so it is unit-testable anywhere.

References: MAVLink common message set,
https://mavlink.io/en/messages/common.html
"""
import math
from dataclasses import dataclass

# MAV_MODE_FLAG_SAFETY_ARMED bit in HEARTBEAT.base_mode
MAV_MODE_FLAG_SAFETY_ARMED = 128


@dataclass
class GlobalPosition:
    latitude: float    # degrees
    longitude: float   # degrees
    altitude_msl: float    # metres above mean sea level
    altitude_rel: float    # metres above the home/takeoff point


def global_position_from_int(lat_degE7: int, lon_degE7: int,
                             alt_mm: int, relative_alt_mm: int) -> GlobalPosition:
    """Convert GLOBAL_POSITION_INT fields (degE7 / millimetres) to SI units."""
    return GlobalPosition(
        latitude=lat_degE7 / 1e7,
        longitude=lon_degE7 / 1e7,
        altitude_msl=alt_mm / 1e3,
        altitude_rel=relative_alt_mm / 1e3,
    )


@dataclass
class BatteryStatus:
    voltage: float     # volts
    current: float     # amps; NaN when the FC reports it as unmeasured
    remaining: float   # fraction 0..1; NaN when unmeasured


def battery_from_sys_status(voltage_battery_mv: int, current_battery_ca: int,
                            battery_remaining_pct: int) -> BatteryStatus:
    """Convert SYS_STATUS battery fields.

    MAVLink uses -1 as the "not measured" sentinel for current (centiamps)
    and remaining (%); map those to NaN rather than a misleading number.
    """
    return BatteryStatus(
        voltage=voltage_battery_mv / 1e3,
        current=math.nan if current_battery_ca == -1 else current_battery_ca / 1e2,
        remaining=math.nan if battery_remaining_pct == -1 else battery_remaining_pct / 100.0,
    )


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Convert ATTITUDE euler angles (radians) to an (x, y, z, w) quaternion."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def is_armed(base_mode: int) -> bool:
    """True when HEARTBEAT.base_mode has the safety-armed flag set."""
    return bool(base_mode & MAV_MODE_FLAG_SAFETY_ARMED)


def gps_fix_ok(fix_type: int) -> bool:
    """True for a usable position fix (GPS_RAW_INT.fix_type >= 3D)."""
    return fix_type >= 3
