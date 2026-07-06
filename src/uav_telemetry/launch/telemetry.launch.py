"""MAVLink telemetry bridge.

    ros2 launch uav_telemetry telemetry.launch.py                          # UDP :14550
    ros2 launch uav_telemetry telemetry.launch.py connection_url:=/dev/ttyACM0
    ros2 launch uav_telemetry telemetry.launch.py use_mock_link:=true     # no aircraft
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('connection_url', default_value='udp:0.0.0.0:14550'),
        DeclareLaunchArgument('use_mock_link', default_value='false'),
        Node(
            package='uav_telemetry',
            executable='mavlink_bridge',
            name='mavlink_bridge',
            output='screen',
            parameters=[{
                'connection_url': LaunchConfiguration('connection_url'),
                'use_mock_link': LaunchConfiguration('use_mock_link'),
            }],
        ),
    ])
