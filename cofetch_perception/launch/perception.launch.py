from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('camera_topic', default_value='/color/preview/image',
                         description='Camera image topic'),
    DeclareLaunchArgument('enable_display', default_value='false',
                         description='Enable OpenCV display'),
]


def generate_launch_description():
    pkg_cofetch_perception = get_package_share_directory('cofetch_perception')
    pkg_cofetch_config = get_package_share_directory('cofetch_config')

    config_file = os.path.join(pkg_cofetch_config, 'config', 'perception_config.yaml')

    object_detection = Node(
        package='cofetch_perception',
        executable='object_detection_node.py',
        name='object_detection',
        output='screen',
        parameters=[{
            'config_file': config_file,
            'camera_topic': LaunchConfiguration('camera_topic'),
            'enable_display': LaunchConfiguration('enable_display'),
        }],
    )

    object_tracking = Node(
        package='cofetch_perception',
        executable='object_tracking_node.py',
        name='object_tracking',
        output='screen',
        parameters=[{
            'max_tracking_distance': 50.0,
            'tracking_timeout': 5.0,
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(object_detection)
    ld.add_action(object_tracking)

    return ld