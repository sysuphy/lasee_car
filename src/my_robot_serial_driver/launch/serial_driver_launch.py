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
    urdf_tutorial_path = get_package_share_directory('my_robot_serial_driver')
    default_model_path = os.path.join(urdf_tutorial_path, 'urdf', 'motor.urdf.xacro')
    default_rviz_config_path = os.path.join(urdf_tutorial_path, 'rviz', 'zhugeliang_car.rviz')

    model_arg = DeclareLaunchArgument(name='model', default_value=str(default_model_path),
                                      description='Absolute path to robot urdf file')
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
                                     description='Absolute path to rviz config file')
    
    robot_description = ParameterValue(Command(['xacro ', LaunchConfiguration('model')]),
                                       value_type=str)
   

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )


    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )


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
