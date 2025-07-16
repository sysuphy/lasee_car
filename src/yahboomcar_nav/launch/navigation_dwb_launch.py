import os
from ament_index_python.packages import get_package_share_path
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import LogInfo
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import TimerAction

def generate_launch_description():
    package_path = get_package_share_directory('yahboomcar_nav')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    urdf_tutorial_path = get_package_share_path('yahboomcar_description')

    default_model_path = urdf_tutorial_path / 'urdf/yahboomcar_R2.urdf'
    default_rviz_config_path = urdf_tutorial_path / 'rviz/yahboomcar.rviz'    

    gui_arg = DeclareLaunchArgument(name='gui', default_value='false', choices=['true', 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    model_arg = DeclareLaunchArgument(name='model', default_value=str(default_model_path),
                                      description='Absolute path to robot urdf file')
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
                                     description='Absolute path to rviz config file')
    
    robot_description = ParameterValue(Command(['xacro ', LaunchConfiguration('model')]),
                                       value_type=str)

    
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    nav2_param_path = LaunchConfiguration('params_file', default=os.path.join(
        package_path, 'params', 'dwb_nav_params.yaml'))
    
    map_yaml_default = os.path.join(package_path, 'maps', 'map.yaml')
    map_yaml_path = LaunchConfiguration('map', default=map_yaml_default)
    


    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-d', LaunchConfiguration('rvizconfig')],
         )
    
    initial_pose_node = TimerAction(
    period=3.0,  # 启动 3 秒后发布
    actions=[
        Node(
            package='yahboomcar_nav',
            executable='initial_pose_pub',
            name='initial_pose_publisher',
            output='screen'
            )
            ]
          )
    send_goal_node = Node(
        package='yahboomcar_nav',
        executable='send_goal',
        name='goal_sender',
        output='screen'
          )


    return LaunchDescription([
        gui_arg,
        model_arg,
        DeclareLaunchArgument('use_sim_time', default_value=use_sim_time,
                              description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('map', default_value=map_yaml_path,
                              description='Full path to map file to load'),
        DeclareLaunchArgument('params_file', default_value=nav2_param_path,
                              description='Full path to param file to load'),
        LogInfo(msg="✅ 地图文件路径为：" + map_yaml_default),
        
        joint_state_publisher_node,
        robot_state_publisher_node, 
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [nav2_bringup_dir, '/launch', '/bringup_launch.py']),
            launch_arguments={
                'map': map_yaml_path,
                'use_sim_time': use_sim_time,
                'params_file': nav2_param_path}.items(),
        ),
        
        rviz_arg,
        rviz_node,
        send_goal_node,
        
    ])
