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
    pkg_cofetch_manipulation = get_package_share_directory('cofetch_manipulation')

    arm_control = Node(
        package='cofetch_manipulation',
        executable='arm_control_node.py',
        name='arm_control',
        output='screen',
        parameters=[{
            'max_velocity': 0.5,
            'max_acceleration': 1.0,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    gripper_control = Node(
        package='cofetch_manipulation',
        executable='gripper_control_node.py',
        name='gripper_control',
        output='screen',
        parameters=[{
            'max_opening': 0.03,
            'max_force': 10.0,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    manipulation_executor = Node(
        package='cofetch_manipulation',
        executable='manipulation_executor_node.py',
        name='manipulation_executor',
        output='screen',
        parameters=[{
            'approach_distance': 0.1,
            'retreat_distance': 0.15,
        }],
        namespace=LaunchConfiguration('robot_name'),
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(arm_control)
    ld.add_action(gripper_control)
    ld.add_action(manipulation_executor)

    return ld