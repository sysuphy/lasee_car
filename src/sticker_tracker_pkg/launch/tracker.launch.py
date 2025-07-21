from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # tracker.launch.py
        Node(
            package='sticker_tracker_pkg',
            executable='sticker_tracker_node',  # 改为实际功能节点
            name='sticker_tracker',
            output='screen'
        )
    ])
