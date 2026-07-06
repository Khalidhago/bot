"""Launch the base controller with its default configuration."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('bot_base'), 'config', 'base.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_mock_hardware', default_value='true',
            description='Simulate the drivetrain instead of opening the serial port'),
        Node(
            package='bot_base',
            executable='base_node',
            name='bot_base',
            output='screen',
            parameters=[
                config,
                {'use_mock_hardware': LaunchConfiguration('use_mock_hardware')},
            ],
        ),
    ])
