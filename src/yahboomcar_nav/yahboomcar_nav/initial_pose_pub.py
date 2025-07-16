import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped


class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__('initial_pose_publisher')
        self.publisher_ = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        timer_period = 2.0  # 发布一次初始位置，2秒后
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.initial_pose_published = False

    def timer_callback(self):
        if self.initial_pose_published:
            return

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()

        # 设置位置（单位：m）
        msg.pose.pose.position.x = 1.0
        msg.pose.pose.position.y = 1.0
        msg.pose.pose.position.z = 0.0

        # 设置朝向（四元数）
        # 例如朝向 0 度（朝正 X 轴）
        from transforms3d.euler import euler2quat
        q = euler2quat(0, 0, math.radians(90))  # yaw = 90.0
        msg.pose.pose.orientation.x = q[1]
        msg.pose.pose.orientation.y = q[2]
        msg.pose.pose.orientation.z = q[3]
        msg.pose.pose.orientation.w = q[0]

        # 设置协方差（AMCL 要求，通常只设置位置和角度的协方差）
        msg.pose.covariance[0] = 0.25  # x方向
        msg.pose.covariance[7] = 0.25  # y方向
        msg.pose.covariance[35] = 0.06853891945200942  # yaw 方向，单位：弧度^2（例如 15 度）

        self.publisher_.publish(msg)
        self.get_logger().info('✅ 已发布初始位置到 /initialpose')
        self.initial_pose_published = True

        # ✅ 打印日志
        self.get_logger().info(
          f'✅ 发布初始位姿: '
          f'位置=({msg.pose.pose.position.x:.2f}, {msg.pose.pose.position.y:.2f}, {msg.pose.pose.position.z:.2f}), '
          f'朝向四元数=({msg.pose.pose.orientation.x:.4f}, {msg.pose.pose.orientation.y:.4f}, '
          f'{msg.pose.pose.orientation.z:.4f}, {msg.pose.pose.orientation.w:.4f})')

def main(args=None):
    rclpy.init(args=args)
    node = InitialPosePublisher()
    rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
