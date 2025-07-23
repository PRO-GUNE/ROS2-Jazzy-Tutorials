from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution, FindExecutable
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = "robot_urdf_himala"  # Replace with your package name

    # Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ),
        launch_arguments={
            'world': PathJoinSubstitution([FindPackageShare(pkg_name), 'worlds', 'four_walls.world']),
            'paused': 'false',
            'use_sim_time': 'true',
            'gui': 'true',
            'headless': 'false',
            'debug': 'false'
        }.items()
    )

    # Robot State Publisher to publish robot_description parameter
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command([
                PathJoinSubstitution([FindExecutable(name='xacro')]),
                ' ',
                PathJoinSubstitution([FindPackageShare(pkg_name), 'urdf', 'four_wheel_robot.xacro'])
            ])
        }]
    )

    # Spawn robot in Gazebo using spawn_entity node from gazebo_ros
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'four_wheel_robot'
        ],
        output='screen'
    )

    # Your random control node
    random_control_node = Node(
        package=pkg_name,
        executable='random_control_node',
        name='random_control_node',
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity_node,
        random_control_node
    ])
