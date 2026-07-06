"""ROS 2 node driving the differential-drive base.

Subscribes:  /cmd_vel (geometry_msgs/Twist)
Publishes:   /odom (nav_msgs/Odometry), /joint_states (sensor_msgs/JointState)
Broadcasts:  odom -> base_footprint TF (optional; disable when an EKF owns it)

Safety: if no cmd_vel arrives within `cmd_vel_timeout` seconds the wheels are
commanded to zero, so a dropped Wi-Fi link to a phone or joystick cannot leave
the robot driving blind.
"""
import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry as OdometryMsg
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster

from bot_base.kinematics import DiffDriveKinematics, Odometry, clamp
from bot_base.motor_driver import MockMotorDriver


class BaseNode(Node):

    def __init__(self):
        super().__init__('bot_base')

        self.declare_parameter('wheel_radius', 0.045)
        self.declare_parameter('wheel_separation', 0.26)
        self.declare_parameter('max_linear_speed', 0.6)     # m/s
        self.declare_parameter('max_angular_speed', 2.5)    # rad/s
        self.declare_parameter('max_wheel_speed', 20.0)     # rad/s
        self.declare_parameter('control_rate', 50.0)        # Hz
        self.declare_parameter('cmd_vel_timeout', 0.5)      # s
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('use_mock_hardware', True)
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('serial_baudrate', 115200)

        p = lambda name: self.get_parameter(name).value
        self._max_linear = p('max_linear_speed')
        self._max_angular = p('max_angular_speed')
        self._timeout = p('cmd_vel_timeout')
        self._publish_tf = p('publish_tf')
        self._odom_frame = p('odom_frame')
        self._base_frame = p('base_frame')

        self._kinematics = DiffDriveKinematics(
            wheel_radius=p('wheel_radius'),
            wheel_separation=p('wheel_separation'),
            max_wheel_speed=p('max_wheel_speed'),
        )
        self._odometry = Odometry(self._kinematics)

        if p('use_mock_hardware'):
            self._driver = MockMotorDriver()
            self.get_logger().info('Using mock motor driver (no hardware)')
        else:
            from bot_base.motor_driver import SerialMotorDriver
            self._driver = SerialMotorDriver(
                port=p('serial_port'), baudrate=p('serial_baudrate'))
            self.get_logger().info(f"Using serial motor driver on {p('serial_port')}")

        self._target = (0.0, 0.0)  # (linear, angular)
        self._last_cmd_time = self.get_clock().now()
        self._last_update_time = self.get_clock().now()
        self._wheel_positions = [0.0, 0.0]  # integrated joint angles, rad

        self._odom_pub = self.create_publisher(OdometryMsg, 'odom', 10)
        self._joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self._tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(Twist, 'cmd_vel', self._on_cmd_vel, 10)

        period = 1.0 / p('control_rate')
        self._timer = self.create_timer(period, self._control_step)

    def _on_cmd_vel(self, msg: Twist) -> None:
        self._target = (
            clamp(msg.linear.x, self._max_linear),
            clamp(msg.angular.z, self._max_angular),
        )
        self._last_cmd_time = self.get_clock().now()

    def _control_step(self) -> None:
        now = self.get_clock().now()
        dt = (now - self._last_update_time).nanoseconds * 1e-9
        self._last_update_time = now

        # Deadman: stop if commands went stale.
        age = (now - self._last_cmd_time).nanoseconds * 1e-9
        linear, angular = (0.0, 0.0) if age > self._timeout else self._target

        left, right = self._kinematics.to_wheel_speeds(linear, angular)
        self._driver.set_wheel_speeds(left, right)

        if isinstance(self._driver, MockMotorDriver):
            self._driver.advance(dt)

        measured_left, measured_right = self._driver.get_wheel_speeds()
        self._odometry.update(measured_left, measured_right, dt)
        self._wheel_positions[0] += measured_left * dt
        self._wheel_positions[1] += measured_right * dt

        self._publish_state(now, measured_left, measured_right)

    def _publish_state(self, now, left_speed: float, right_speed: float) -> None:
        stamp = now.to_msg()
        odom = self._odometry

        qz = math.sin(odom.heading / 2.0)
        qw = math.cos(odom.heading / 2.0)

        msg = OdometryMsg()
        msg.header.stamp = stamp
        msg.header.frame_id = self._odom_frame
        msg.child_frame_id = self._base_frame
        msg.pose.pose.position.x = odom.x
        msg.pose.pose.position.y = odom.y
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw
        msg.twist.twist.linear.x = odom.linear_velocity
        msg.twist.twist.angular.z = odom.angular_velocity
        # Fixed covariance tuned for wheel odometry; diagonal only.
        msg.pose.covariance[0] = msg.pose.covariance[7] = 1e-3
        msg.pose.covariance[35] = 1e-2
        msg.twist.covariance[0] = msg.twist.covariance[7] = 1e-3
        msg.twist.covariance[35] = 1e-2
        self._odom_pub.publish(msg)

        joints = JointState()
        joints.header.stamp = stamp
        joints.name = ['left_wheel_joint', 'right_wheel_joint']
        joints.position = list(self._wheel_positions)
        joints.velocity = [left_speed, right_speed]
        self._joint_pub.publish(joints)

        if self._publish_tf:
            tf = TransformStamped()
            tf.header.stamp = stamp
            tf.header.frame_id = self._odom_frame
            tf.child_frame_id = self._base_frame
            tf.transform.translation.x = odom.x
            tf.transform.translation.y = odom.y
            tf.transform.rotation.z = qz
            tf.transform.rotation.w = qw
            self._tf_broadcaster.sendTransform(tf)

    def destroy_node(self):
        self._driver.stop()
        self._driver.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BaseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
