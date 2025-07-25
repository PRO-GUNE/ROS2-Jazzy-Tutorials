# ROS2-Jazzy-Tutorials
A repository containing tutorials for ROS2 Jazzy release with a focus on Robotics projects and labs.

## Prerequisites
You should have the following installed:
- ROS2 Jazzy
- Gazebo

## URDF
This section contains tutorials related to URDF (Unified Robot Description Format) files, which are used to describe the physical properties of a robot.
- **URDF Basics**: An introduction to URDF, its structure, and how to create a simple URDF file.
- **URDF with Gazebo**: A tutorial on how to use URDF files with Gazebo for simulation.

Create a package for this robot as we've discussed in previous sessions. Within the package directory, create a folder named `urdf` and place the URDF file inside it. Use the same file names for your ease. If you choose different filenames make sure to make changes appropriately in all required files including the launch files. The structure of the packages should look like this:

```
your_package/
├── urdf/
│   └── robot.xacro
│   └── robot.gazebo
├── launch/
│   └── your_robot.launch.py
├── src/
│   └── your_robot_node.cpp
├── worlds/
│   └── four_walls.world
├── package.xml
└── CMakeLists.txt
```

The files in the `robot` directory in this branch contain partially completed URDF files. You can use these as a starting point for your own robot. The final output should be a complete URDF file that describes a four-wheeled robot with a camera, a sonar sensor and a lidar sensor.

Next you should write a control node to make the robot randomly traverse within a four walled area without making any collisions. This should be done from scratch using the values taken from the sensors by subscribing to the topics. You can control the robot using the `geometry_msgs/Twist` message type. The node should subscribe to the camera, sonar and lidar topics and publish to the `cmd_vel` topic.

Finally, to launch the robot in Gazebo you should create a launch file. A partially completed launch file is provided in the `launch` directory. You can use this as a starting point for your own launch file. The final output should be a launch file that launches the robot in Gazebo with the URDF file and the control node.


## Tasks
1. **Create a URDF file**: Create a URDF file for a four-wheeled robot with a camera, sonar sensor, and lidar sensor.
2. **Write a control node**: Write a control node that makes the robot randomly traverse within a four-walled area without making any collisions.
3. **Create a launch file**: Create a launch file that launches the robot in Gazebo with the URDF file and the control node.
4. **Test the robot**: Test the robot in Gazebo and make sure it is working as expected.
5. **Document the process**: Document the process of creating the URDF file, control node, and launch file. Include any challenges faced and how they were overcome.

