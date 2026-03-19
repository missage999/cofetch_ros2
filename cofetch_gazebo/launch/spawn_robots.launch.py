from ament_index_python.packages import get_package_share_directory

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('robot1_x', default_value='0',
                          description='Robot 1 X position'),
    DeclareLaunchArgument('robot1_y', default_value='0',
                          description='Robot 1 Y position'),
    DeclareLaunchArgument('robot2_x', default_value='2',
                          description='Robot 2 X position'),
    DeclareLaunchArgument('robot2_y', default_value='2',
                          description='Robot 2 Y position'),
]


def generate_launch_description():
    pkg_cofetch_desc = get_package_share_directory('cofetch_description')

    xacro_file = PathJoinSubstitution([
        pkg_cofetch_desc,
        'urdf',
        'cofetch_robot.urdf.xacro'
    ])

    world_file = PathJoinSubstitution([
        pkg_cofetch_desc,
        'worlds',
        'indoor.world'
    ])

    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo_models_path = os.path.join(pkg_cofetch_desc, 'worlds')

    set_env_vars = [
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gazebo_models_path),
    ]

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={'GZ_SIM_RESOURCE_PATH': gazebo_models_path},
    )

    ld = LaunchDescription(ARGUMENTS)
    for env_var in set_env_vars:
        ld.add_action(env_var)
    ld.add_action(gz_sim)

    return ld