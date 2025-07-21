#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped, PointStamped
from rclpy.duration import Duration
from std_msgs.msg import Bool
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

import math
import numpy as np
import time
from time import sleep

RAD2DEG = 180 / math.pi

class LaserObjectTracker(Node):
    def __init__(self,name):
        super().__init__(name)
        #create a sub
        self.sub_laser = self.create_subscription(LaserScan,"/scan",self.registerScan,1)
        # 发布当前是否处于追踪状态
        #self.pub_active = self.create_publisher(Bool, '/laser_tracking/active', 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.priorityAngle = 30.0  # 前方高优先区角度范围 ±30°
        self.ResponseDist = 3.0    # 识别的最大距离
        self.laserAngle = 90.0     # 整个感知角度范围
        self.navigator_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info("等待 bt_navigator 服务器启动中...")
        self.navigator_client.wait_for_server(timeout_sec=10.0)
        self.get_logger().info("bt_navigator 服务器已就绪")

    def registerScan(self, scan_data):
        if not isinstance(scan_data, LaserScan): return
        ranges = np.array(scan_data.ranges)
        offset = 0.5
        frontDistList = []
        frontDistIDList = []
        minDistList = []
        minDistIDList = []

        
        for i in range(len(ranges)):
            angle = (scan_data.angle_min + scan_data.angle_increment * i) * RAD2DEG
            if abs(angle) < self.priorityAngle:
                if ranges[i] < (self.ResponseDist + offset):
                    frontDistList.append(ranges[i])
                    frontDistIDList.append(angle)
            elif abs(angle) > self.priorityAngle and abs(angle) < self.laserAngle and ranges[i] != 0.0:
                minDistList.append(ranges[i])
                minDistIDList.append(angle)
            
                
        if len(frontDistIDList) != 0:
            minDist = min(frontDistList)
            minDistID = frontDistIDList[frontDistList.index(minDist)]
        elif len(minDistIDList) != 0:
            minDist = min(minDistList)
            minDistID = minDistIDList[minDistList.index(minDist)]
        else:
            self.get_logger().info("未检测到任何物体，跳过处理")
            return
        
        if minDistID != -1:
            self.process_and_send_goal(minDist, minDistID)

    def process_and_send_goal(self, minDist, minDistID):
    # 极坐标转换为笛卡尔坐标（在 laser_link 下）：
        x_laser = minDist * math.cos(math.radians(minDistID))
        y_laser = minDist * math.sin(math.radians(minDistID))
    # 构造 laser_link 下的点
        laser_point = PointStamped()
        laser_point.header.frame_id = "laser"
        laser_point.header.stamp = self.get_clock().now().to_msg()
        laser_point.point.x = x_laser
        laser_point.point.y = y_laser
        laser_point.point.z = 0.0

        try:
        # 查询转换到 map 坐标系
            map_point = self.tf_buffer.transform(laser_point, "map", timeout=Duration(seconds=0.5))
            target_x = map_point.point.x
            target_y = map_point.point.y
        # 与上一次目标比较距离，避免频繁发出
            now = time.time()
            if not hasattr(self, 'last_goal_time'):
               self.last_goal_time = 0
            if self.prev_goal is None or self.get_distance(self.prev_goal, (target_x, target_y)) > 0.3 or now - self.last_goal_time > 10:
               self.prev_goal = (target_x, target_y)
               self.last_goal_time = now
               self.send_goal(target_x, target_y)
            else:
               self.get_logger().info("目标变化不大，跳过发布")

        except Exception as e:
               self.get_logger().warn(f"TF Transform failed: {e}")  
    def send_goal_to_bt_navigator(self, pose: PoseStamped):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info("Sending goal to bt_navigator...")
        self._send_goal_future = self.navigator_client.send_goal_async(goal_msg)

    def send_goal(self, x, y):
        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = 'map'
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0.0
        goal.pose.orientation.w = 1.0  # 朝向不重要，可设为默认

        self.send_goal_to_bt_navigator(goal)
        self.get_logger().info(f"导航目标发送: ({x:.2f}, {y:.2f})")

    def get_distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def main(args=None):
    rclpy.init(args=args)
    node = LaserObjectTracker("laser_tracker")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()

        