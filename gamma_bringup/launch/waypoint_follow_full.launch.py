from launch import LaunchDescription
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
import os
from launch.actions import ExecuteProcess, TimerAction


def generate_launch_description():

    return LaunchDescription([

        
        # Node(
        #     package='wayp_plan_tools',
        #     executable='waypoint_loader',
        #     name='wayp_load',
        #     output='screen',
        #     parameters=[
        #         #{"file_dir": pkg_dir + "/csv"},
        #         {"file_dir": "/home/dev/waypoints/"},
        #         {"file_name": "saved_waypoints_mod.csv"},
        #         {"per_waypoint_display": 5}, # display speed every 5th waypoint
        #     ],
        # ),
       Node(
            package='wayp_plan_tools',
            executable='waypoint_to_target',
            name='wayp_to_target',
            output='screen',
            parameters=[
                {"lookahead_min": 8.5},
                {"lookahead_max": 12.0},
                {"mps_alpha": 3.5},
                {"mps_beta": 5.5},
                {"waypoint_topic": "waypointarray"},
                {"tf_frame_id": "gamma1/base_link"},
                {"tf_child_frame_id": "map"},
            ],
        ),
        TimerAction (period = 2.0, actions= 
       [Node(
            package='wayp_plan_tools',
            executable='single_goal_pursuit',
            name='pure_pursuit',
            output='screen',
            parameters=[
                {"cmd_topic": "cmd_vel"},
                {"wheelbase": 3.900},
                {"waypoint_topic": "targetpoints"},
            ])],
        ),
        TimerAction (period = 5.0, actions= 
        [ExecuteProcess(
            cmd=['ros2','topic','pub','--once', 'control_reinit','std_msgs/msg/Bool',"{data: {true}}"],output='screen')]),


        Node(
            package='gamma_bringup',
            executable='publisher_node',
            name='crio_publisher',
            output='screen',
        ),
        TimerAction (period = 4.0, actions=
        [ExecuteProcess(
            cmd=['ros2','topic','pub','--once', 'aut_dat','std_msgs/msg/Bool',"{data: {true}}"],output='screen')]),
        TimerAction( period = 6.0, actions=
        [ExecuteProcess(
            cmd=['ros2','topic','pub','--once', 'aut_sys','std_msgs/msg/Bool',"{data: {true}}"],output='screen')]),
            




    ])