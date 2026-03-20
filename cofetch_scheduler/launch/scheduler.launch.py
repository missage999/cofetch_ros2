from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('auto_generation', default_value='true',
                         description='Enable automatic task generation'),
]


def generate_launch_description():
    pkg_cofetch_scheduler = get_package_share_directory('cofetch_scheduler')
    pkg_cofetch_config = get_package_share_directory('cofetch_config')

    config_file = os.path.join(pkg_cofetch_config, 'config', 'scheduler_config.yaml')

    task_generation = Node(
        package='cofetch_scheduler',
        executable='task_generation_node.py',
        name='task_generation',
        output='screen',
        parameters=[{
            'auto_generation': LaunchConfiguration('auto_generation'),
            'generation_interval': 2.0,
        }],
    )

    task_assignment = Node(
        package='cofetch_scheduler',
        executable='task_assignment_node.py',
        name='task_assignment',
        output='screen',
        parameters=[{
            'assignment_strategy': 'nearest',
            'load_balancing': True,
            'max_tasks_per_robot': 5,
        }],
    )

    task_monitor = Node(
        package='cofetch_scheduler',
        executable='task_execution_monitor_node.py',
        name='task_execution_monitor',
        output='screen',
        parameters=[{
            'check_interval': 1.0,
            'failure_timeout': 60.0,
            'max_retries': 3,
        }],
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(task_generation)
    ld.add_action(task_assignment)
    ld.add_action(task_monitor)

    return ld