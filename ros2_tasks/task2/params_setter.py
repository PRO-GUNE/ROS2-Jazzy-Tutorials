#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class ParamsSetter(Node):
    def __init__(self):
        super().__init__('params_setter')
        
        # Define parameter name and value
        param = 'global_parameter'
        value = 'default_value'
        
        # Set global parameter
        self.declare_parameter(param, value)
        self.set_parameters([rclpy.parameter.Parameter(param, rclpy.Parameter.Type.STRING, value)])
        
        self.get_logger().info(f'Set parameter "{param}" with value "{value}"')

def main(args=None):
    rclpy.init(args=args)
    node = ParamsSetter()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()