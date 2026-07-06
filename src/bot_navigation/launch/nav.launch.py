"""Autonomous navigation on a saved map using the standard Nav2 bringup.

Nav2's final output lands on /cmd_vel (nav2_bringup default), which the twist
mux in bot_bringup consumes as its lowest-priority input — teleop always wins
before anything reaches the base on /cmd_vel_base.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    nav2_launch_dir = os.path.join(
        get_package_share_directory('nav2_bringup'), 'launch')
    params = os.path.join(
        get_package_share_directory('bot_navigation'), 'config', 'nav2_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('map', description='Full path to the map yaml file'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_launch_dir, 'bringup_launch.py')),
            launch_arguments={
                'map': LaunchConfiguration('map'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': params,
            }.items(),
        ),
    ])
