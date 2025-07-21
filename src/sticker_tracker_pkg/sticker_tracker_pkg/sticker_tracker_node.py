# ROS2 Foxy 节点：贴纸检测并通过串口通信发送中心点坐标
# 功能：检测白色贴纸区域的中心点，判断激光点是否进入区域，持续2秒后发送"WIN"

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import time
import serial

class StickerTracker(Node):
    def __init__(self):
        super().__init__('sticker_tracker')

        self.cap = cv2.VideoCapture(0)

        # 串口设置（树莓派上可能是 /dev/ttyUSB0 或 /dev/ttyACM0）
        SERIAL_PORT = '/dev/ttyACM0'
        BAUD_RATE = 9600
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.get_logger().info(f"串口连接成功：{SERIAL_PORT}")
        except Exception as e:
            self.get_logger().error(f"串口连接失败: {e}")
            self.ser = None

        # HSV范围设置
        self.white_lower = np.array([100, 20, 115])
        self.white_upper = np.array([112, 40, 135])
        self.laser_pt = (620, 360)

        self.in_target_since = None
        self.victory_flag = False

        # 定时器以固定频率运行（30Hz）
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_white = cv2.inRange(hsv, self.white_lower, self.white_upper)
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        white_center = None
        white_box = None

        if contours:
            max_cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_cnt)
            if area > 300:
                x, y, w, h = cv2.boundingRect(max_cnt)
                cx, cy = x + w // 2, y + h // 2
                white_center = (cx, cy)
                white_box = (x, y, w, h)

                self.get_logger().info(f"白色贴纸中心点：{white_center}")

                # 发送坐标
                if self.ser:
                    try:
                        self.ser.write(f"{cx},{cy}\n".encode())
                    except:
                        self.get_logger().error("串口写入失败")

        # 激光点在框内并持续2秒判断
        if white_box:
            x, y, w, h = white_box
            if x <= self.laser_pt[0] <= x + w and y <= self.laser_pt[1] <= y + h:
                if self.in_target_since is None:
                    self.in_target_since = time.time()
                else:
                    duration = time.time() - self.in_target_since
                    if duration >= 2 and not self.victory_flag:
                        self.get_logger().info("\U0001F3AF 激光对准目标超过2秒，胜利！")
                        self.victory_flag = True
                        if self.ser:
                            try:
                                self.ser.write(b"WIN\n")
                            except:
                                self.get_logger().error("串口写入失败")
            else:
                self.in_target_since = None
        else:
            self.in_target_since = None

        # 可视化调试（树莓派可注释掉）
        cv2.circle(frame, self.laser_pt, 6, (0, 0, 255), -1)
        if white_box:
            cv2.rectangle(frame, (white_box[0], white_box[1]), (white_box[0]+white_box[2], white_box[1]+white_box[3]), (0, 255, 0), 2)
        if white_center:
            cv2.circle(frame, white_center, 6, (0, 255, 0), -1)
        cv2.imshow("Tracking", frame)
        cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        if self.ser:
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = StickerTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
