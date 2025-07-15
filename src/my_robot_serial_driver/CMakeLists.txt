cmake_minimum_required(VERSION 3.5)
project(my_robot_serial_driver)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclpy REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

include_directories(include)

add_executable(serial_driver_node src/serial_driver_node.cpp)
ament_target_dependencies(serial_driver_node rclcpp geometry_msgs)

install(TARGETS
  serial_driver_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME})
  
# 安装 Python 脚本
install(PROGRAMS
  src/odom_publisher_node.py
  DESTINATION lib/${PROJECT_NAME}
)


ament_package()
