"""Phone teleoperation: rosbridge websocket plus the static web UI server."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('http_port', default_value='8080',
                              description='Port for the joystick web page'),
        DeclareLaunchArgument('ws_port', default_value='9090',
                              description='Port for the rosbridge websocket'),
        Node(
            package='rosbridge_server',
            executable='rosbridge_websocket',
            name='rosbridge_websocket',
            output='screen',
            parameters=[{'port': LaunchConfiguration('ws_port')}],
        ),
        Node(
            package='bot_mobile_bridge',
            executable='web_server',
            name='mobile_web_server',
            output='screen',
            parameters=[{'port': LaunchConfiguration('http_port')}],
        ),
    ])
