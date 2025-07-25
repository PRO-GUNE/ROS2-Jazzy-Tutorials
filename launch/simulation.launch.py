from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_name = FindPackageShare("pkg_name")

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
                    "paused": "TODO: Provide the correct value",
                    "use_sim_time": "TODO: Provide the correct value",
                    "gui": "TODO: Provide the correct value",
                    "headless": "TODO: Provide the correct value",
                    "debug": "TODO: Provide the correct value",
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
            # TODO: Spawn the robot in Gazebo
            # Spawn robot in Gazebo
        ]
    )
