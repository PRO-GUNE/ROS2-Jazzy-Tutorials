from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_name = FindPackageShare("robot_model_pkg")

    # Xacro command to generate URDF
    xacro_command = [
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([pkg_name, "urdf", "robot.xacro"]),
    ]

    return LaunchDescription(
        [
            # TODO: Create the control node
            # Node
            Node(
                package="robot_model_pkg",
                executable="random_mover",
                name="random_mover_node",
                output="screen",
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

                # TODO: Provide the correct values for the argumentsarguments
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
            
            # Robot description parameter
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "param",
                    "set",
                    "/robot_state_publisher",
                    "robot_description",
                    PathJoinSubstitution([FindExecutable(name="xacro")]),
                    PathJoinSubstitution([pkg_name, "urdf", "robot.xacro"]),
                ],
                shell=True,
            ),
            # TODO: Create the robot state publisher node
            # Robot state publisher
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": xacro_command}],
            ),
            # TODO: Spawn the robot in Gazebo
            # Spawn robot in Gazebo
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                name="spawn_entity",
                output="screen",
                arguments=[
                    "-entity",
                    "four_wheel_robot",
                    "-topic",
                    "robot_description",
                    "-x",
                    "0.0",
                    "-y",
                    "0.0",
                    "-z",
                    "0.1",  # Adjust the height as needed
                    "-entity", "robot_model_pkg",
                ],
            ),
        ]
    )
