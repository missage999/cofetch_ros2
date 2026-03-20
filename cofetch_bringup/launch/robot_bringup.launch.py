from ament_index_python.packages import get_package_share_directory
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


ARGUMENTS = [
    DeclareLaunchArgument('robot_name', default_value='robot1',
                         description='Robot name'),
    DeclareLaunchArgument('use_sim_time', default_value='true',
                         choices=['true', 'false'],
                         description='Use simulation time'),
    DeclareLaunchArgument('world_file', default_value='',
                         description='Gazebo world file'),
]


def generate_launch_description():
    pkg_cofetch_gazebo = get_package_share_directory('cofetch_gazebo')
    pkg_cofetch_config = get_package_share_directory('cofetch_config')
    pkg_cofetch_perception = get_package_share_directory('cofetch_perception')
    pkg_cofetch_exploration = get_package_share_directory('cofetch_exploration')
    pkg_cofetch_navigation = get_package_share_directory('cofetch_navigation')
    pkg_cofetch_manipulation = get_package_share_directory('cofetch_manipulation')
    pkg_cofetch_scheduler = get_package_share_directory('cofetch_scheduler')

    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_gazebo, '/launch/gazebo.launch.py'
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'robot_name': LaunchConfiguration('robot_name'),
        }.items(),
    )

    config_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_config, '/launch/config.launch.py'
        ]),
    )

    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_perception, '/launch/perception.launch.py'
        ]),
    )

    exploration_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_exploration, '/launch/exploration.launch.py'
        ]),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name'),
        }.items(),
    )

    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_navigation, '/launch/navigation.launch.py'
        ]),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name'),
        }.items(),
    )

    manipulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_manipulation, '/launch/manipulation.launch.py'
        ]),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name'),
        }.items(),
    )

    scheduler_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_scheduler, '/launch/scheduler.launch.py'
        ]),
    )

    delayed_config = TimerAction(
        period=2.0,
        actions=[config_launch]
    )

    delayed_scheduler = TimerAction(
        period=3.0,
        actions=[scheduler_launch]
    )

    delayed_perception = TimerAction(
        period=4.0,
        actions=[perception_launch]
    )

    delayed_navigation = TimerAction(
        period=5.0,
        actions=[navigation_launch]
    )

    delayed_manipulation = TimerAction(
        period=5.5,
        actions=[manipulation_launch]
    )

    delayed_exploration = TimerAction(
        period=6.0,
        actions=[exploration_launch]
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gazebo_launch)
    ld.add_action(delayed_config)
    ld.add_action(delayed_scheduler)
    ld.add_action(delayed_perception)
    ld.add_action(delayed_navigation)
    ld.add_action(delayed_manipulation)
    ld.add_action(delayed_exploration)

    return ld