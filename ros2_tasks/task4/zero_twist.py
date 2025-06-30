#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class ZeroTwist(Node):
    def __init__(self):
        super().__init__('zero_twist')
        
        # Subscriber to is_stopped topic
        self.subscription = self.create_subscription(
            String,
            'is_stopped',
            self.is_stopped_callback,
            10
        )
        
        # Publisher for twist with queue_size=10
        self.publisher = self.create_publisher(Twist, 'twist', 10)
        
        self.get_logger().info('Zero twist node started')

    def is_stopped_callback(self, msg):
        if msg.data.lower() == 'true':
            # Publish zero twist message
            zero_twist = Twist()
            zero_twist.linear.x = 0.0
            zero_twist.linear.y = 0.0
            zero_twist.linear.z = 0.0
            zero_twist.angular.x = 0.0
            zero_twist.angular.y = 0.0
            zero_twist.angular.z = 0.0
            
            self.publisher.publish(zero_twist)
            self.get_logger().info('Published zero twist message')
        else:
            self.get_logger().info('Received false, not publishing')

def main(args=None):
    rclpy.init(args=args)
    node = ZeroTwist()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()