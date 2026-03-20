from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('robot_name', default_value='robot1',
                         description='Robot name'),
]


def generate_launch_description():
    pkg_cofetch_navigation = get_package_share_directory('cofetch_navigation')
    pkg_cofetch_config = get_package_share_directory('cofetch_config')

    config_file = os.path.join(pkg_cofetch_config, 'config', 'navigation_config.yaml')

    pure_pursuit = Node(
        package='cofetch_navigation',
        executable='pure_pursuit_controller.py',
        name='pure_pursuit_controller',
        output='screen',
        parameters=[{
            'lookahead_distance': 0.5,
            'target_velocity': 0.3,
            'max_angular_velocity': 1.5,
            'goal_tolerance': 0.1,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    obstacle_avoidance = Node(
        package='cofetch_navigation',
        executable='obstacle_avoidance_node.py',
        name='obstacle_avoidance',
        output='screen',
        parameters=[{
            'safety_distance': 0.3,
            'detection_range': 1.0,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(pure_pursuit)
    ld.add_action(obstacle_avoidance)

    return ld