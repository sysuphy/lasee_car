#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from transforms3d.euler import euler2quat
import serial
import math


class OdomPublisher(Node):
    def __init__(self):
        super().__init__('odom_publisher')

        # === 声明参数（带默认值） ===
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 9600)
        self.declare_parameter('wheel_separation', 0.182)
        self.declare_parameter('wheel_radius', 0.0325)
        self.declare_parameter('ticks_per_rev', 1728)
        self.declare_parameter('update_rate', 20.0)  # Hz

        # === 读取参数 ===
        port = self.get_parameter('port').get_parameter_value().string_value
        baud = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.WHEEL_BASE = self.get_parameter('wheel_separation').value
        self.WHEEL_RADIUS = self.get_parameter('wheel_radius').value
        self.TICKS_PER_REV = self.get_parameter('ticks_per_rev').value
        update_rate = self.get_parameter('update_rate').value

        # === 打开串口 ===
        try:
            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.get_logger().info(f"Serial driver initialized on {port} @ {baud}bps")
        except Exception as e:
            self.get_logger().error(f"Failed to open serial port {port}: {e}")
            raise

        # === 发布器 ===
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # === 状态变量 ===
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_left_ticks = 0
        self.last_right_ticks = 0
        self.first_read = True
        self.last_time = self.get_clock().now()

        # === 启动定时器（读取串口）===
        self.timer = self.create_timer(1.0 / update_rate, self.read_serial)

    def read_serial(self):
        try:
           now = self.get_clock().now()
           dt = (now - self.last_time).nanoseconds / 1e9
           self.last_time = now

           # 模拟编码器跳变
           fake_left = self.last_left_ticks + 10
           fake_right = self.last_right_ticks + 12  # 模拟轻微转向
           self.update_odometry(fake_left, fake_right, dt, now)

           self.get_logger().info("✅ 模拟数据已发送。")
        except Exception as e:
           self.get_logger().error(f"Serial read error: {e}")



    def update_odometry(self, left_ticks, right_ticks, dt, now):
        delta_left = left_ticks - self.last_left_ticks
        delta_right = right_ticks - self.last_right_ticks
        self.get_logger().info(f"编码器差值: left={delta_left}, right={delta_right}")

        left_dist = 2 * math.pi * self.WHEEL_RADIUS * (delta_left / self.TICKS_PER_REV)
        right_dist = 2 * math.pi * self.WHEEL_RADIUS * (delta_right / self.TICKS_PER_REV)

        delta_s = (left_dist + right_dist) / 2.0
        delta_theta = (right_dist - left_dist) / self.WHEEL_BASE

        dx = delta_s * math.cos(self.theta + delta_theta / 2.0)
        dy = delta_s * math.sin(self.theta + delta_theta / 2.0)

        self.x += dx
        self.y += dy
        self.theta += delta_theta

        qw, qx, qy, qz = euler2quat(0, 0, self.theta)

        # 发布 odom
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = delta_s / dt
        odom.twist.twist.angular.z = delta_theta / dt
        self.odom_pub.publish(odom)

        # 发布 TF
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        self.last_left_ticks = left_ticks
        self.last_right_ticks = right_ticks


def main(args=None):
    rclpy.init(args=args)
    node = OdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt. Exiting...")
    finally:
        node.serial_port.close()
        node.destroy_node()
        rclpy.shutdown()
if __name__ == "__main__":
    main()