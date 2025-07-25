from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_name = FindPackageShare("robot_model_pkg")  # Updated package name

    # Xacro command to generate URDF
    xacro_command = [
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([pkg_name, "urdf", "robot.xacro"]),
    ]

    return LaunchDescription(
        [
            # Robot Control Node
            Node(
                package='robot_model_pkg',
                executable='robot_control_node.py',
                name='robot_control_node',
                output='screen',
                parameters=[
                    {'use_sim_time': True}
                ]
            ),
            # Load Gazebo world
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [
                                FindPackageShare("gazebo_ros"),
                                "launch",
                                "gazebo.launch.py",
                            ]
                        )
                    ]
                ),
                # Launch arguments for Gazebo
                launch_arguments={
                    "world": PathJoinSubstitution(
                        [pkg_name, "worlds", "four_walls.world"]
                    ),
                    "paused": "false",
                    "use_sim_time": "true",
                    "gui": "true",
                    "headless": "false",
                    "debug": "false",
                }.items(),
            ),
            # Robot state publisher
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[
                    {'use_sim_time': True},
                    {'robot_description': xacro_command}
                ]
            ),
            
            # Joint state publisher
            Node(
                package='joint_state_publisher',
                executable='joint_state_publisher',
                name='joint_state_publisher',
                output='screen',
                parameters=[{'use_sim_time': True}]
            ),
            
            # Spawn robot in Gazebo
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                name='spawn_robot',
                output='screen',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'four_wheel_robot',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.5'
                ],
                parameters=[{'use_sim_time': True}]
            ),
        ]
    )
