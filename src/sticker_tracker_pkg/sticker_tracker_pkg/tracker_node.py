#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TrackerNode(Node):
    def __init__(self):
        super().__init__('tracker_node')
        self.get_logger().info('Sticker Tracker Node has started.')

    def timer_callback(self):
        self.get_logger().info('Tracking sticker...')

def main(args=None):
    rclpy.init(args=args)
    node = TrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
