"""Visualise the robot model in RViz with a joint state GUI."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('bot_description')
    urdf_path = os.path.join(pkg_share, 'urdf', 'bot.urdf.xacro')
    rviz_config = os.path.join(pkg_share, 'rviz', 'display.rviz')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true',
                              description='Start RViz and the joint state GUI'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('gui')),
        ),
    ])
