"""Full robot bringup: model, base controller, command mux, phone teleop.

    ros2 launch bot_bringup robot.launch.py                      # real hardware
    ros2 launch bot_bringup robot.launch.py use_mock_hardware:=true
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_share = get_package_share_directory('bot_description')
    base_share = get_package_share_directory('bot_base')
    bridge_share = get_package_share_directory('bot_mobile_bridge')
    bringup_share = get_package_share_directory('bot_bringup')

    urdf_path = os.path.join(description_share, 'urdf', 'bot.urdf.xacro')
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_mock_hardware', default_value='false',
            description='Simulate the drivetrain instead of opening the serial port'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),

        # Base node instantiated directly (not via base.launch.py) so its
        # cmd_vel input can be rewired behind the twist mux.
        Node(
            package='bot_base',
            executable='base_node',
            name='bot_base',
            output='screen',
            parameters=[
                os.path.join(base_share, 'config', 'base.yaml'),
                {'use_mock_hardware': LaunchConfiguration('use_mock_hardware')},
            ],
            remappings=[('cmd_vel', 'cmd_vel_base')],
        ),

        Node(
            package='twist_mux',
            executable='twist_mux',
            output='screen',
            parameters=[os.path.join(bringup_share, 'config', 'twist_mux.yaml')],
            remappings=[('cmd_vel_out', 'cmd_vel_base')],
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(bridge_share, 'launch', 'mobile.launch.py')),
        ),
    ])
