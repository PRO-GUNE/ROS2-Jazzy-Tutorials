from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = FindPackageShare("suhan_urdf")

    # Robot description using xacro
    robot_description = Command([
        "xacro ",
        PathJoinSubstitution([pkg_name, "urdf", "robot.xacro"])
    ])

    return LaunchDescription([
        # Load Gazebo world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare("gazebo_ros"),
                    "launch",
                    "gazebo.launch.py",
                ])
            ]),
            launch_arguments={
                "world": PathJoinSubstitution([pkg_name, "worlds", "gazebo_four_walls.world"]),
                "paused": "false",
                "use_sim_time": "true",
                "gui": "true",
                "headless": "false",
                "debug": "false",
            }.items(),
        ),

        # Robot state publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}]
        ),

        # Joint state publisher (if you have movable joints)
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}]
        ),

        # Spawn robot in Gazebo
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            name="spawn_entity",
            output="screen",
            arguments=[
                "-topic", "robot_description",
                "-entity", "robot",
            ],
        ),
    ])