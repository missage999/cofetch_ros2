from ament_index_python.packages import get_package_share_directory

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('robot_name', default_value='cofetch_robot1',
                          description='Robot name'),
    DeclareLaunchArgument('namespace', default_value='/',
                          description='Robot namespace'),
]


def generate_launch_description():
    pkg_cofetch_desc = get_package_share_directory('cofetch_description')
    pkg_turtlebot4 = get_package_share_directory('turtlebot4_description')
    pkg_irobot = get_package_share_directory('irobot_create_description')
    pkg_nav2_minimal = get_package_share_directory('nav2_minimal_tb4_description')

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
    robot_name = LaunchConfiguration('robot_name')
    namespace = LaunchConfiguration('namespace')

    model_paths = f"{pkg_cofetch_desc}/worlds:{pkg_turtlebot4}/meshes:{pkg_irobot}/meshes:{pkg_nav2_minimal}/meshes"

    set_env_vars = [
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', pkg_cofetch_desc + '/worlds'),
        SetEnvironmentVariable('GZ_SIM_MODEL_PATH', model_paths),
    ]

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': Command([
                'xacro ', xacro_file
            ]),
        }],
        namespace=namespace,
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        namespace=namespace,
    )

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={
            'GZ_SIM_RESOURCE_PATH': pkg_cofetch_desc + '/worlds',
            'GZ_SIM_MODEL_PATH': model_paths,
        },
    )

    delayed_spawn = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                name='spawn_entity',
                output='screen',
                arguments=[
                    '-name', robot_name,
                    '-topic', 'robot_description',
                    '-x', '0', '-y', '0', '-z', '0',
                    '-namespace', namespace,
                ],
                parameters=[{'use_sim_time': use_sim_time}],
            )
        ]
    )

    ld = LaunchDescription(ARGUMENTS)
    for env_var in set_env_vars:
        ld.add_action(env_var)
    ld.add_action(robot_state_publisher)
    ld.add_action(joint_state_publisher)
    ld.add_action(gz_sim)
    ld.add_action(delayed_spawn)

    return ld