from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('log_level', default_value='info',
                         choices=['debug', 'info', 'warn', 'error'],
                         description='Log level'),
    DeclareLaunchArgument('heartbeat_timeout', default_value='5.0',
                         description='Robot heartbeat timeout in seconds'),
]


def generate_launch_description():
    system_monitor = Node(
        package='cofetch_monitoring',
        executable='system_monitor_node.py',
        name='system_monitor',
        output='screen',
        parameters=[{
            'log_level': LaunchConfiguration('log_level'),
            'heartbeat_timeout': float(LaunchConfiguration('heartbeat_timeout')),
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(system_monitor)

    return ld