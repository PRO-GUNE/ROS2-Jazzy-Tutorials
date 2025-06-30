#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import csv
import os

class TwistFromDatabase(Node):
    def __init__(self):
        super().__init__('twist_from_database')
        
        # Publisher with queue_size=20
        self.publisher = self.create_publisher(Twist, 'twist_from_database', 20)
        
        # Timer for 10Hz rate
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # Load CSV data
        self.twist_data = []
        self.current_index = 0
        self.load_csv_data()
        
        self.get_logger().info('Twist from database node started')

    def load_csv_data(self):
        try:
            csv_file_path = os.path.join(os.path.dirname(__file__), 'values.csv')
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 6:
                        # Parse linear x,y,z and angular x,y,z
                        linear_x, linear_y, linear_z, angular_x, angular_y, angular_z = map(float, row)
                        self.twist_data.append({
                            'linear': [linear_x, linear_y, linear_z],
                            'angular': [angular_x, angular_y, angular_z]
                        })
            self.get_logger().info(f'Loaded {len(self.twist_data)} twist messages from CSV')
        except FileNotFoundError:
            self.get_logger().error('values.csv file not found')
        except Exception as e:
            self.get_logger().error(f'Error reading CSV: {str(e)}')

    def timer_callback(self):
        if self.twist_data and self.current_index < len(self.twist_data):
            twist_msg = Twist()
            data = self.twist_data[self.current_index]
            
            twist_msg.linear.x = data['linear'][0]
            twist_msg.linear.y = data['linear'][1]
            twist_msg.linear.z = data['linear'][2]
            twist_msg.angular.x = data['angular'][0]
            twist_msg.angular.y = data['angular'][1]
            twist_msg.angular.z = data['angular'][2]
            
            self.publisher.publish(twist_msg)
            self.get_logger().info(f'Published twist message {self.current_index + 1}')
            
            self.current_index += 1
        else:
            # Reset to beginning or stop
            self.current_index = 0

def main(args=None):
    rclpy.init(args=args)
    node = TwistFromDatabase()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()