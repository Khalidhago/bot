"""Online SLAM with slam_toolbox. Drive the robot around (phone joystick works
well for this) and save the map with `ros2 run nav2_map_server map_saver_cli`.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('bot_navigation'), 'config', 'slam_toolbox.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                config,
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ],
        ),
    ])
