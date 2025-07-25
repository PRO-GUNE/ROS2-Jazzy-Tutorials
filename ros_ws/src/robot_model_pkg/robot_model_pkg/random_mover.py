import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import random

class RandomMoveNode(Node):
    def __init__(self):
        super().__init__('random_mover')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.move_randomly)

    def move_randomly(self):
        twist = Twist()
        twist.linear.x = random.uniform(0.0, 0.4)
        twist.angular.z = random.uniform(-1.0, 1.0)
        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = RandomMoveNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
