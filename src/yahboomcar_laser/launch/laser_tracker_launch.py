from launch import LaunchDescription
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
         get_package_share_directory('ydlidar_ros2_driver'), 'launch'),
         '/ydlidar_launch.py'])
      )

    laser_tracker_node = Node(
        package='yahboomcar_laser',
        executable='laser_tracker',
    )

    bringup_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
        get_package_share_directory('my_robot_serial_driver'), 'launch'),
        '/serial_driver_launch.py'])
    )

    launch_description = LaunchDescription([
        lidar_node,
        laser_tracker_node,
        bringup_node
        ]) 
    return launch_description
