from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.actions import (RegisterEventHandler, EmitEvent, LogInfo)
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from launch.events import matches_action
import lifecycle_msgs.msg


def generate_launch_description():
    return LaunchDescription([
        # static tf
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/tf_static.launch.py'])
        ),
        # Drivers
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch/drivers', '/gps_duro_reference.launch.py'])
        ),
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch/drivers', '/can_pacmod3.launch.xml'])
        ),
        # General nodes
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/3d_marker.launch.py'])
        ),
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/foxglove_bridge_launch.xml'])
        ),
        TimerAction(
            period=2.0, # delay
            actions=[
                Node(
                    package='lexus_bringup',
                    executable='path_steering_and_kmph',
                    name='path_steering_and_kmph_d',
                    output='screen',
                    parameters=[{"marker_color": "b", "path_size": 550}]
                ), 
            ]),
        # Control nodes   
        # TimerAction(
        #     period=2.0, # delay
        #     actions=[
        #         IncludeLaunchDescription(
        #             PythonLaunchDescriptionSource([
        #                 FindPackageShare("lexus_bringup"), '/launch', '/speed_control.launch.py'])
        #         ),
        #     ]),     
        Node(
            package='rviz_2d_overlay_plugins',
            executable='string_to_overlay_text',
            name='string_to_overlay_text_ctr_status',
            output='screen',
            parameters=[
                {"string_topic": "/lexus3/control_status"},
                {"fg_color": "r"}, # colors can be: r,g,b,w,k,p,y (red,green,blue,white,black,pink,yellow)
            ],
        ),  
        ## LIDAR(s)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch/drivers', '/os_64_center_b.launch.py'])
        ),

        # TODO: instead of TimerAction delay
        # RegisterEventHandler(
        # OnStateTransition(
        #     target_lifecycle_node=lexus3/os_center/os_sensor, 
        #     goal_state='inactive',
        #     entities=[LogInfo(msg="xxxxxxxxxxxxxxxxxxxxxxxxxxxxx os_sensor activating..."),])
        # ),

        # TimerAction(
        #     period=0.0, # delay
        #     actions=[        
        #     IncludeLaunchDescription(
        #         PythonLaunchDescriptionSource([
        #             FindPackageShare("lexus_bringup"), '/launch/drivers', '/os_32_right_b.launch.py'])
        #     ),        
        # ]),
      
        ## egyetemi palya
        Node(
            package='gui_lexus',
            executable='pub_lane_markers',
            name='pub_lane_markers_1',
            output='screen',
        ),
    ])
