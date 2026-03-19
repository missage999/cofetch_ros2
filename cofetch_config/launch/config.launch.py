from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('config_dir', default_value='',
                          description='Configuration directory path'),
]


def generate_launch_description():
    pkg_cofetch_config = get_package_share_directory('cofetch_config')

    default_config_dir = os.path.join(pkg_cofetch_config, 'config')

    config_manager = Node(
        package='cofetch_config',
        executable='config_manager.py',
        name='config_manager',
        output='screen',
        parameters=[{
            'config_dir': LaunchConfiguration('config_dir'),
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(config_manager)

    return ld