#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Package name - replace 'robot_model_pkg' with your actual package name
    package_name = 'robot_model_pkg'
    
    # Get package directories
    pkg_share = FindPackageShare(package=package_name).find(package_name)
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')
    
    # Set paths to different files and folders
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.xacro')
    world_file = os.path.join(pkg_share, 'worlds', 'four_walls.world')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'robot.rviz')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_gui = LaunchConfiguration('use_gui')
    headless = LaunchConfiguration('headless')
    world = LaunchConfiguration('world')
    
    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='true',
        description='Whether to start RVIZ'
    )
    
    declare_use_gui_cmd = DeclareLaunchArgument(
        name='use_gui',
        default_value='true',
        description='Whether to execute gzclient'
    )
    
    declare_headless_cmd = DeclareLaunchArgument(
        name='headless',
        default_value='false',
        description='Whether to run Gazebo in headless mode'
    )
    
    declare_world_cmd = DeclareLaunchArgument(
        name='world',
        default_value=world_file,
        description='Full path to world file to load'
    )
    
    # Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': open(urdf_file).read()}
        ]
    )
    
    # Joint State Publisher Node
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': world,
            'gui': use_gui,
            'headless': headless,
            'verbose': 'true'
        }.items()
    )
    
    # Spawn Robot Entity
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'four_wheel_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # RVIZ Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        condition=IfCondition(use_rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Robot Control Node (your custom control node)
    robot_control_node = Node(
        package=package_name,
        executable='robot_node',  # Make sure this matches your executable name in CMakeLists.txt
        name='robot_control_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('cmd_vel', 'cmd_vel'),
            ('camera', 'sensor/camera'),
            ('sonar', 'sensor/sonar'),
            ('lidar', 'sensor/lidar')
        ]
    )
    
    # Transform from base_link to camera_link_optical for camera
    camera_optical_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_optical_tf',
        arguments=['0', '0', '0', '-1.5708', '0', '-1.5708', 'camera_link', 'camera_link_optical'],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Transform from base_link to laser_frame for lidar
    laser_frame_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_frame_tf',
        arguments=['0', '0', '0', '0', '0', '0', 'lidar_link', 'laser_frame'],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Create the launch description and populate
    ld = LaunchDescription()
    
    # Add launch arguments
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_use_gui_cmd)
    ld.add_action(declare_headless_cmd)
    ld.add_action(declare_world_cmd)
    
    # Add nodes
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(gazebo_launch)
    ld.add_action(spawn_entity_node)
    ld.add_action(rviz_node)
    ld.add_action(robot_control_node)
    ld.add_action(camera_optical_tf)
    ld.add_action(laser_frame_tf)
    
    return ld