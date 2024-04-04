from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='demo_jkk',
            executable='odometry_from_twist',
            parameters=[{
                "status_topic": "/lexus3/vehicle_status",
                # "status_topic": "/nissan9/vehicle_status",
                "odom_child_frame_id": "/lexus3/odom",
                # "odom_child_frame_id": "/nissan9/odom",
                "map_frame_id" : "/map",
                "wheelbase": 2.789,
                # "wheelbase": 2.7,
            }]
        )
    ])