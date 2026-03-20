from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('robot_name', default_value='robot1',
                         description='Robot name'),
    DeclareLaunchArgument('map_resolution', default_value='0.05',
                         description='Map resolution'),
]


def generate_launch_description():
    pkg_cofetch_config = get_package_share_directory('cofetch_config')
    config_file = os.path.join(pkg_cofetch_config, 'config', 'exploration_config.yaml')

    frontier_detection = Node(
        package='cofetch_exploration',
        executable='frontier_detection_node.py',
        name='frontier_detection',
        output='screen',
        parameters=[{
            'map_resolution': 0.05,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    exploration_coordinator = Node(
        package='cofetch_exploration',
        executable='exploration_coordinator_node.py',
        name='exploration_coordinator',
        output='screen',
        parameters=[{
            'exploration_timeout': 600.0,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    collaboration = Node(
        package='cofetch_exploration',
        executable='exploration_collaboration_node.py',
        name='exploration_collaboration',
        output='screen',
        parameters=[{
            'shared_map_enabled': True,
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(frontier_detection)
    ld.add_action(exploration_coordinator)
    ld.add_action(collaboration)

    return ld