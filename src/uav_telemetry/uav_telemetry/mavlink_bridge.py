"""MAVLink -> ROS 2 telemetry bridge.

Connects to a PX4/ArduPilot flight controller (serial, UDP or TCP — anything
pymavlink accepts as a connection string) and republishes core telemetry as
standard ROS topics, so the rest of the stack — and any ground-station or
web dashboard via rosbridge — sees the aircraft with zero MAVLink knowledge.

Publishes:
    ~/global_position   sensor_msgs/NavSatFix
    ~/battery           sensor_msgs/BatteryState
    ~/attitude          sensor_msgs/Imu           (orientation only)
    ~/armed             std_msgs/Bool
    ~/flight_mode       std_msgs/String

With `use_mock_link:=true` a built-in simulated aircraft is used instead of
a real connection — same philosophy as bot_base's mock motor driver: the
whole stack must run on a desk.
"""
import math
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState, Imu, NavSatFix, NavSatStatus
from std_msgs.msg import Bool, String

from uav_telemetry import converters


class MockLink:
    """Simulated aircraft: slowly orbits a point, drains its battery."""

    def __init__(self):
        self._t = 0.0

    def poll(self, dt: float) -> dict:
        self._t += dt
        angle = 0.05 * self._t
        return {
            'position': converters.GlobalPosition(
                latitude=47.397742 + 3e-5 * math.sin(angle),
                longitude=8.545594 + 3e-5 * math.cos(angle),
                altitude_msl=488.0 + 30.0,
                altitude_rel=30.0,
            ),
            'battery': converters.BatteryStatus(
                voltage=16.8 - 0.005 * self._t,
                current=12.0,
                remaining=max(0.0, 1.0 - self._t / 1200.0),
            ),
            'quaternion': converters.quaternion_from_euler(0.0, 0.0, angle),
            'armed': True,
            'mode': 'AUTO.LOITER',
            'fix_ok': True,
        }


class MavlinkLink:
    """Real link: background thread drains the MAVLink stream, keeping the
    latest value of each message type; poll() snapshots them."""

    def __init__(self, url: str, logger):
        from pymavlink import mavutil
        self._logger = logger
        self._conn = mavutil.mavlink_connection(url)
        self._lock = threading.Lock()
        self._state = {}
        self._running = True
        threading.Thread(target=self._read_loop, daemon=True).start()
        logger.info(f'Waiting for heartbeat on {url} ...')

    def _read_loop(self):
        while self._running:
            msg = self._conn.recv_match(blocking=True, timeout=1.0)
            if msg is None:
                continue
            kind = msg.get_type()
            with self._lock:
                if kind == 'GLOBAL_POSITION_INT':
                    self._state['position'] = converters.global_position_from_int(
                        msg.lat, msg.lon, msg.alt, msg.relative_alt)
                elif kind == 'SYS_STATUS':
                    self._state['battery'] = converters.battery_from_sys_status(
                        msg.voltage_battery, msg.current_battery, msg.battery_remaining)
                elif kind == 'ATTITUDE':
                    self._state['quaternion'] = converters.quaternion_from_euler(
                        msg.roll, msg.pitch, msg.yaw)
                elif kind == 'HEARTBEAT':
                    self._state['armed'] = converters.is_armed(msg.base_mode)
                    self._state['mode'] = self._conn.flightmode
                elif kind == 'GPS_RAW_INT':
                    self._state['fix_ok'] = converters.gps_fix_ok(msg.fix_type)

    def poll(self, dt: float) -> dict:
        with self._lock:
            return dict(self._state)

    def close(self):
        self._running = False
        self._conn.close()


class MavlinkBridge(Node):

    def __init__(self):
        super().__init__('mavlink_bridge')
        self.declare_parameter('connection_url', 'udp:0.0.0.0:14550')
        self.declare_parameter('use_mock_link', False)
        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('frame_id', 'uav_link')

        self._frame_id = self.get_parameter('frame_id').value

        if self.get_parameter('use_mock_link').value:
            self._link = MockLink()
            self.get_logger().info('Using mock MAVLink source (no aircraft)')
        else:
            self._link = MavlinkLink(
                self.get_parameter('connection_url').value, self.get_logger())

        self._pub_fix = self.create_publisher(NavSatFix, '~/global_position', 10)
        self._pub_batt = self.create_publisher(BatteryState, '~/battery', 10)
        self._pub_att = self.create_publisher(Imu, '~/attitude', 10)
        self._pub_armed = self.create_publisher(Bool, '~/armed', 10)
        self._pub_mode = self.create_publisher(String, '~/flight_mode', 10)

        period = 1.0 / self.get_parameter('publish_rate').value
        self._timer = self.create_timer(period, lambda: self._publish(period))

    def _publish(self, dt: float) -> None:
        state = self._link.poll(dt)
        stamp = self.get_clock().now().to_msg()

        if 'position' in state:
            pos = state['position']
            fix = NavSatFix()
            fix.header.stamp = stamp
            fix.header.frame_id = self._frame_id
            fix.status.status = (NavSatStatus.STATUS_FIX if state.get('fix_ok')
                                 else NavSatStatus.STATUS_NO_FIX)
            fix.latitude = pos.latitude
            fix.longitude = pos.longitude
            fix.altitude = pos.altitude_msl
            self._pub_fix.publish(fix)

        if 'battery' in state:
            batt = state['battery']
            msg = BatteryState()
            msg.header.stamp = stamp
            msg.voltage = batt.voltage
            msg.current = batt.current
            msg.percentage = batt.remaining
            msg.present = True
            self._pub_batt.publish(msg)

        if 'quaternion' in state:
            x, y, z, w = state['quaternion']
            imu = Imu()
            imu.header.stamp = stamp
            imu.header.frame_id = self._frame_id
            imu.orientation.x = x
            imu.orientation.y = y
            imu.orientation.z = z
            imu.orientation.w = w
            self._pub_att.publish(imu)

        if 'armed' in state:
            self._pub_armed.publish(Bool(data=state['armed']))
        if 'mode' in state and state['mode']:
            self._pub_mode.publish(String(data=str(state['mode'])))

    def destroy_node(self):
        if hasattr(self._link, 'close'):
            self._link.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MavlinkBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
