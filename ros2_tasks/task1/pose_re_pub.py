#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose

class PoseRepublisher(Node):
    def __init__(self):
        super().__init__('pose_re_pub')
        
        # Subscriber to PoseWithCovarianceStamped
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            'pose_with_covariance_stamped',
            self.pose_callback,
            10
        )
        
        # Publisher for Pose
        self.publisher = self.create_publisher(Pose, 'pose', 10)
        
        self.get_logger().info('Pose republisher node started')

    def pose_callback(self, msg):
        # Extract pose from PoseWithCovarianceStamped and republish
        pose_msg = Pose()
        pose_msg.position = msg.pose.pose.position
        pose_msg.orientation = msg.pose.pose.orientation
        
        self.publisher.publish(pose_msg)
        self.get_logger().info('Republished pose message')

def main(args=None):
    rclpy.init(args=args)
    node = PoseRepublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()