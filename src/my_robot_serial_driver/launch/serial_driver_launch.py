import serial
from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

import os
from ament_index_python.packages import get_package_share_directory

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='my_robot_serial_driver',
            executable='serial_driver_node',
            name='serial_driver',
            parameters=[{
                'port': '/dev/ttyACM0',
                'baudrate': 9600
            }]
        ),
        Node(
             package='my_robot_serial_driver',
             executable='odom_publisher_node.py',
             name='odom_publisher',
             parameters=[os.path.join(get_package_share_directory('my_robot_serial_driver'), 'config', 'params.yaml')],
             output='screen'
      ),
          
    ])
