from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("topic", description="a topic to process"),
        Node(
            package='time_utils',
            executable='display_time',
            output='screen',
            parameters=[
                {
                    'topic': LaunchConfiguration("topic")
                }
            ]
        )
    ])