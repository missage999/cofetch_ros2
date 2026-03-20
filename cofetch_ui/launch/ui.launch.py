from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('update_rate', default_value='1.0',
                         description='Status update rate'),
]


def generate_launch_description():
    status_display = Node(
        package='cofetch_ui',
        executable='status_display_node.py',
        name='status_display',
        output='screen',
        parameters=[{
            'update_rate': float(LaunchConfiguration('update_rate')),
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(status_display)

    return ld