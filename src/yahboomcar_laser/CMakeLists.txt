cmake_minimum_required(VERSION 3.5)
project(yahboomcar_laser)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# 安装 Python 脚本为可执行节点
install(PROGRAMS
  yahboomcar_laser/laser_tracker.py
  DESTINATION lib/${PROJECT_NAME}
)

# 安装 launch、config 等目录
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
