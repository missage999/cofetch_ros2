from ament_index_python.packages import get_package_share_directory

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import ExecutableInPackage


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('world_file', default_value='',
                          description='Gazebo world file'),
    DeclareLaunchArgument('robot_name', default_value='cofetch_robot1',
                          description='Robot name'),
    DeclareLaunchArgument('namespace', default_value='/',
                          description='Robot namespace'),
]


def generate_launch_description():
    pkg_cofetch_desc = get_package_share_directory('cofetch_description')
    pkg_cofetch_gazebo = get_package_share_directory('cofetch_gazebo')

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

    gazebo_models_path = os.path.join(pkg_cofetch_desc, 'worlds')

    set_env_vars = [
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gazebo_models_path),
    ]

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': Command([
                'xacro ', xacro_file, ' ',
                'gazebo:=ignition', ' ',
                'namespace:=', namespace
            ]),
        }],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        namespace=namespace,
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ],
        namespace=namespace,
    )

    gz_sim_pkg = get_package_share_directory('ros_gz_sim')

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={'GZ_SIM_RESOURCE_PATH': gazebo_models_path},
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-name', robot_name,
            '-file', xacro_file,
            '-x', '0', '-y', '0', '-z', '0',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    ld = LaunchDescription(ARGUMENTS)
    for env_var in set_env_vars:
        ld.add_action(env_var)
    ld.add_action(robot_state_publisher)
    ld.add_action(joint_state_publisher)
    ld.add_action(gz_sim)
    ld.add_action(spawn_entity)

    return ld