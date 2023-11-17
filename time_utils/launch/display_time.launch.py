from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    return LaunchDescription([
        ## TODO: ros2 launch time_utils display_time.launch.py topic:=other_topic
        DeclareLaunchArgument("topic", description="a topic to process"),
        Node(
            package='time_utils',
            executable='display_time',
            output='screen',
            parameters=[
                {'topic': '/drone1/gps/duro/time_ref'}
            ]
        )
    ])