#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import random

class WanderBot(Node):
    def __init__(self):
        super().__init__('wander_bot')
        self.velocity_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.lidar_listener = self.create_subscription(LaserScan, 'sensor/lidar', self.lidar_callback, 10)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.is_obstacle_ahead = False
        self.is_turning = False
        self.turn_steps_remaining = 0

    def lidar_callback(self, scan_msg):
        # Analyze the lidar scan in the forward direction (center +/- 20 samples)
        center = len(scan_msg.ranges) // 2
        forward_window = scan_msg.ranges[center - 20 : center + 20]
        min_distance = min(forward_window)
        self.is_obstacle_ahead = min_distance < 0.7

    def control_loop(self):
        cmd = Twist()
        if self.is_turning:
            cmd.angular.z = self.turn_direction
            self.turn_steps_remaining -= 1
            if self.turn_steps_remaining <= 0:
                self.is_turning = False
        elif self.is_obstacle_ahead:
            # Initiate a random turn
            self.is_turning = True
            self.turn_steps_remaining = random.randint(10, 30)
            self.turn_direction = random.choice([-1.0, 1.0])
            cmd.angular.z = self.turn_direction
        else:
            cmd.linear.x = 0.3  # Move forward
        self.velocity_publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = WanderBot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main() 