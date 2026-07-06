"""Robot bringup plus Nav2 autonomous navigation on a saved map.

    ros2 launch bot_bringup nav.launch.py map:=/path/to/map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_share = get_package_share_directory('bot_bringup')
    nav_share = get_package_share_directory('bot_navigation')

    return LaunchDescription([
        DeclareLaunchArgument('map', description='Full path to the map yaml file'),
        DeclareLaunchArgument('use_mock_hardware', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bringup_share, 'launch', 'robot.launch.py')),
            launch_arguments={
                'use_mock_hardware': LaunchConfiguration('use_mock_hardware'),
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav_share, 'launch', 'nav.launch.py')),
            launch_arguments={
                'map': LaunchConfiguration('map'),
            }.items(),
        ),
    ])
