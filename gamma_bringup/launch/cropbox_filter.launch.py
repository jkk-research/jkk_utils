from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


# This is the launch file for the filter node, run this file e.g. with:
# ros2 launch arj_simple_perception filter_a.launch.py  
#  cloud_topic:=/lexus3/os_center/points minX:=0.0 maxX:=40.0 minZ:=-2.0 maxZ:=-0.15

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false') # if simulation or ros2 bag (mcap) is used, this should be true
    pkg_name = 'arj_simple_perception'


    return LaunchDescription([
        DeclareLaunchArgument('cloud_topic', default_value="/gamma1/os_center/point", description="a pointcloud topic to process",),
        DeclareLaunchArgument('cloud_frame', default_value="/gamma1/TMF", description="a pointcloud topic to process, default is the topic's own frame",),
        DeclareLaunchArgument('minX', default_value="-40.0", description="minimum x value to filter",),
        DeclareLaunchArgument('maxX', default_value="4.0", description="maximum x value to filter",),
        DeclareLaunchArgument('maxY', default_value="+5.0", description="maximum y value to filter",),
        DeclareLaunchArgument('minY', default_value="-5.0", description="minimum y value to filter",),
        DeclareLaunchArgument('minZ', default_value="-2.0", description="minimum z value to filter",),
        DeclareLaunchArgument('maxZ', default_value="-0.15", description="maximum z value to filter",),
        Node(
            package=pkg_name,
            executable='lidar_filter_simple_param',
            output='screen',
            parameters=[
                {'cloud_topic': "/gamma1/sensing/lidar/concatenated/pointcloud"},
                {'cloud_frame': "/gamma1/TMF"},
                {'minX': 5.0},
                {'minY': -50.0},
                {'minZ': -2.5},
                {'maxX': 50.0},
                {'maxY': 50.0},
                {'maxZ': 5.0},
                {'use_sim_time': False},
            ],
        ),
    ])
