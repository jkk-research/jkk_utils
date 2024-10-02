from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():


    return LaunchDescription([
        Node(
            package='wayp_plan_tools',
            executable='waypoint_loader',
            namespace='lexus3',
            output='screen',
            parameters=[
                {"file_dir": "/mnt/bag/waypoints"},
                {"file_name": "gyor09kocka.csv"},
                {"per_waypoint_display": 5}, # display speed every 5th waypoint 
            ],
        )
    ])