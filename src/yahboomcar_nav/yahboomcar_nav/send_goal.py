#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class GoalSender(Node):
    def __init__(self):
        super().__init__('goal_sender')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.timer = self.create_timer(2.0, self.send_goal)  # 延时2秒发送
        self.goal_sent = False

    def send_goal(self):
        if self.goal_sent:
            return

        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().warn('❌ NavigateToPose action server not available.')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        # 设置导航目标位置（单位：米）
        goal_msg.pose.pose.position.x = 3.0
        goal_msg.pose.pose.position.y = 3.0
        #goal_msg.pose.pose.orientation.w = 1.0  # 朝向角度 = 0°

        self.get_logger().info(' 发送导航目标:x=3.0, y=3')
        self._action_client.send_goal_async(goal_msg)

        self.goal_sent = True


def main(args=None):
    rclpy.init(args=args)
    node = GoalSender()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
