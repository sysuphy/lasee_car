import cv2


def pick_hsv_value(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if frame is not None:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = hsv_frame[y, x]
            print(f"HSV value at point ({x}, {y}): H={h}, S={s}, V={v}")


# 打开摄像头
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 创建窗口并设置鼠标回调函数
cv2.namedWindow('Camera Feed')
cv2.setMouseCallback('Camera Feed', pick_hsv_value)

frame = None  # 初始化frame变量

while True:
    # 读取一帧视频
    ret, frame = cap.read()

    # 检查是否成功读取帧
    if not ret:
        print("无法获取帧，退出...")
        break

    # 显示当前帧
    cv2.imshow('Camera Feed', frame)

    # 按ESC键退出循环
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

# 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()