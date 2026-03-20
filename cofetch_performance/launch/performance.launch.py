from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('monitoring_interval', default_value='1.0',
                         description='Performance monitoring interval'),
]


def generate_launch_description():
    performance_monitor = Node(
        package='cofetch_performance',
        executable='performance_monitor_node.py',
        name='performance_monitor',
        output='screen',
        parameters=[{
            'monitoring_interval': float(LaunchConfiguration('monitoring_interval')),
        }],
    )

    bandwidth_analyzer = Node(
        package='cofetch_performance',
        executable='topic_bandwidth_analyzer.py',
        name='topic_bandwidth_analyzer',
        output='screen',
        parameters=[{
            'analyze_interval': 5.0,
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(performance_monitor)
    ld.add_action(bandwidth_analyzer)

    return ld