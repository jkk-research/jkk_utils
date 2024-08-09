from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():


    return LaunchDescription([
        Node(
            package='wayp_plan_tools',
            executable='waypoint_loader_with_stops',
            namespace='lexus3',
            output='screen',
            parameters=[
                {"file_dir": "/mnt/bag/waypoints"},
                {"file_name": "gyor07durosingle.csv"},
                {"per_waypoint_display": 5}, # display speed every 5th waypoint 
                {"stop_interval": 20.0}, # stop every X meters
                {"stop_decceleration": 0.2}, #  m/s^2
                {"start_acceleration": 0.2}, #  m/s^2
            ],
        )
    ])