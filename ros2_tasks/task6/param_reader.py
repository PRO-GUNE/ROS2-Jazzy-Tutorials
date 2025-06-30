#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class ParamReader(Node):
    def __init__(self):
        super().__init__('param_reader')
        
        # Read parameter from /robot_name
        try:
            # Create a client to get parameter from another node
            self.declare_parameter('robot_name', 'default_robot')
            robot_name = self.get_parameter('robot_name').get_parameter_value().string_value
            
            print(f"Robot name parameter: {robot_name}")
            self.get_logger().info(f'Robot name: {robot_name}')
            
        except Exception as e:
            self.get_logger().error(f'Failed to read robot_name parameter: {str(e)}')
            print("Failed to read robot_name parameter")

def main(args=None):
    rclpy.init(args=args)
    node = ParamReader()
    
    try:
        rclpy.spin_once(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()