import os

from pathlib import Path
from launch import LaunchDescription
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.actions import DeclareLaunchArgument 
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    container_name_arg = DeclareLaunchArgument('pointcloud_container_name', default_value='pointcloud_container')

    config = os.path.join(
        get_package_share_directory('pointcloud_manager'),
        'config',
        'params.yaml'
    )

    container = ComposableNodeContainer(
        name=LaunchConfiguration('pointcloud_container_name'),
        package='rclcpp_components',
        executable='component_container',
        namespace="",
        output='both',
        composable_node_descriptions=[
            ComposableNode(
                package='pointcloud_manager',
                plugin='pointcloud_merger::PCLMerger',
                name="pointcloud_merger",
                parameters=[config],
                extra_arguments=[{'use_intra_process_comms': True}],
            )
        ]
    )

    return LaunchDescription([
        container_name_arg,
        container,
    ])