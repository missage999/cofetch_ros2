from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


ARGUMENTS = [
    DeclareLaunchArgument('num_robots', default_value='2',
                         description='Number of robots'),
]


def generate_launch_description():
    pkg_cofetch_gazebo = get_package_share_directory('cofetch_gazebo')
    pkg_cofetch_bringup = get_package_share_directory('cofetch_bringup')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_gazebo, '/launch/spawn_robots.launch.py'
        ]),
    )

    robot1_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_bringup, '/launch/robot_bringup.launch.py'
        ]),
        launch_arguments={
            'robot_name': 'robot1',
        }.items(),
    )

    robot2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_cofetch_bringup, '/launch/robot_bringup.launch.py'
        ]),
        launch_arguments={
            'robot_name': 'robot2',
        }.items(),
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gazebo_launch)
    ld.add_action(robot1_bringup)
    ld.add_action(robot2_bringup)

    return ld