#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image, Range, LaserScan
from cv_bridge import CvBridge
import cv2
import numpy as np
import random
import math

class RobotControlNode(Node):
    def __init__(self):
        super().__init__('robot_control_node')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Subscribers
        self.camera_sub = self.create_subscription(
            Image, 'sensor/camera', self.camera_callback, 10)
        self.sonar_sub = self.create_subscription(
            Range, 'sensor/sonar', self.sonar_callback, 10)
        self.lidar_sub = self.create_subscription(
            LaserScan, 'sensor/lidar', self.lidar_callback, 10)
        
        # Control timer
        self.control_timer = self.create_timer(0.1, self.control_callback)
        
        # Initialize sensor data
        self.camera_data = None
        self.sonar_data = None
        self.lidar_data = None
        
        # CV Bridge for image processing
        self.bridge = CvBridge()
        
        # Control parameters
        self.linear_vel = 0.5  # m/s
        self.angular_vel = 0.8  # rad/s
        self.safe_distance = 0.8  # meters
        self.min_distance = 0.5  # meters
        
        # State variables
        self.current_direction = 0.0  # Current angular direction
        self.avoid_mode = False
        self.turn_direction = 1  # 1 for left, -1 for right
        self.random_turn_counter = 0
        self.max_random_turns = 50  # Change direction every 5 seconds
        
        self.get_logger().info('Robot Control Node Started')

    def camera_callback(self, msg):
        """Process camera data for visual obstacle detection"""
        try:
            # Convert ROS image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.camera_data = cv_image
            
            # Simple obstacle detection using edge detection
            # This can be enhanced with more sophisticated computer vision
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Check for obstacles in the center region of the image
            height, width = edges.shape
            center_region = edges[int(height*0.3):int(height*0.7), 
                                int(width*0.3):int(width*0.7)]
            
            # If too many edges detected in center, there might be an obstacle
            if np.sum(center_region) > 5000:  # Threshold for obstacle detection
                self.visual_obstacle_detected = True
            else:
                self.visual_obstacle_detected = False
                
        except Exception as e:
            self.get_logger().error(f'Camera callback error: {str(e)}')

    def sonar_callback(self, msg):
        """Process sonar data for close-range obstacle detection"""
        self.sonar_data = msg
        self.get_logger().debug(f'Sonar range: {msg.range:.2f}m')

    def lidar_callback(self, msg):
        """Process lidar data for 360-degree obstacle detection"""
        self.lidar_data = msg
        
        # Log lidar data for debugging
        if len(msg.ranges) > 0:
            min_range = min([r for r in msg.ranges if not math.isinf(r) and not math.isnan(r)])
            self.get_logger().debug(f'Lidar min range: {min_range:.2f}m')

    def get_obstacle_distances(self):
        """Get obstacle distances from all sensors"""
        distances = {
            'front': float('inf'),
            'left': float('inf'),
            'right': float('inf'),
            'back': float('inf')
        }
        
        if self.lidar_data and len(self.lidar_data.ranges) > 0:
            ranges = self.lidar_data.ranges
            num_ranges = len(ranges)
            
            # Divide lidar data into sectors
            sector_size = num_ranges // 4
            
            # Front sector (0 degrees ± 45 degrees)
            front_ranges = (ranges[:sector_size//2] + 
                          ranges[num_ranges-sector_size//2:])
            if front_ranges:
                distances['front'] = min([r for r in front_ranges 
                                        if not math.isinf(r) and not math.isnan(r)])
            
            # Right sector (270 degrees ± 45 degrees)
            right_ranges = ranges[sector_size//2:sector_size + sector_size//2]
            if right_ranges:
                distances['right'] = min([r for r in right_ranges 
                                        if not math.isinf(r) and not math.isnan(r)])
            
            # Back sector (180 degrees ± 45 degrees)
            back_ranges = ranges[sector_size + sector_size//2:2*sector_size + sector_size//2]
            if back_ranges:
                distances['back'] = min([r for r in back_ranges 
                                       if not math.isinf(r) and not math.isnan(r)])
            
            # Left sector (90 degrees ± 45 degrees)
            left_ranges = ranges[2*sector_size + sector_size//2:3*sector_size + sector_size//2]
            if left_ranges:
                distances['left'] = min([r for r in left_ranges 
                                       if not math.isinf(r) and not math.isnan(r)])
        
        # Use sonar data for front distance if available and closer
        if self.sonar_data and not math.isinf(self.sonar_data.range):
            distances['front'] = min(distances['front'], self.sonar_data.range)
        
        return distances

    def control_callback(self):
        """Main control loop for robot navigation"""
        if not self.lidar_data:
            self.get_logger().warn('Waiting for sensor data...')
            return
        
        # Get obstacle distances
        distances = self.get_obstacle_distances()
        
        # Create Twist message
        twist = Twist()
        
        # Check for immediate danger (very close obstacles)
        front_clear = distances['front'] > self.min_distance
        left_clear = distances['left'] > self.min_distance
        right_clear = distances['right'] > self.min_distance
        
        self.get_logger().debug(
            f'Distances - Front: {distances["front"]:.2f}, '
            f'Left: {distances["left"]:.2f}, Right: {distances["right"]:.2f}'
        )
        
        # Emergency stop if obstacle is too close in front
        if distances['front'] < self.min_distance:
            self.get_logger().warn('Emergency stop - obstacle too close!')
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.avoid_mode = True
        
        # Avoidance behavior
        elif not front_clear or distances['front'] < self.safe_distance:
            self.get_logger().info('Obstacle detected - avoiding')
            self.avoid_mode = True
            
            # Stop forward movement
            twist.linear.x = 0.0
            
            # Choose turn direction based on which side has more space
            if distances['left'] > distances['right']:
                twist.angular.z = self.angular_vel  # Turn left
                self.get_logger().info('Turning left to avoid obstacle')
            else:
                twist.angular.z = -self.angular_vel  # Turn right
                self.get_logger().info('Turning right to avoid obstacle')
        
        # Normal movement when path is clear
        else:
            self.avoid_mode = False
            
            # Move forward
            twist.linear.x = self.linear_vel
            
            # Add some random turning for exploration
            self.random_turn_counter += 1
            
            if self.random_turn_counter > self.max_random_turns:
                # Randomly change direction occasionally
                self.current_direction = random.uniform(-0.3, 0.3)
                self.random_turn_counter = 0
                self.get_logger().info(f'Random direction change: {self.current_direction:.2f}')
            
            twist.angular.z = self.current_direction
        
        # Publish command
        self.cmd_vel_pub.publish(twist)
        
        # Log current action
        if twist.linear.x > 0:
            if abs(twist.angular.z) > 0.1:
                action = f"Moving forward and turning {twist.angular.z:.2f}"
            else:
                action = "Moving forward"
        elif abs(twist.angular.z) > 0.1:
            direction = "left" if twist.angular.z > 0 else "right"
            action = f"Turning {direction}"
        else:
            action = "Stopped"
        
        self.get_logger().debug(f'Action: {action}')

def main(args=None):
    rclpy.init(args=args)
    
    try:
        robot_control_node = RobotControlNode()
        rclpy.spin(robot_control_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
