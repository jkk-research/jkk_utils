from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():

    #pkg_name = 'drone_bringup'
    #pkg_dir = os.popen('/bin/bash -c "source /usr/share/colcon_cd/function/colcon_cd.sh && colcon_cd %s && pwd"' % pkg_name).read().strip()

    namespace = "drone1"

    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='gyor0_tf_publisher',
            output='screen',
            ##  Old-style arguments are deprecated, parameters should be used, but this does not work TODO
            arguments=['697237.0', '5285644.0', '0.0','0', '0', '0', '1','map','map_gyor_0'],
            #parameters=[{'translation.x': 697237.0, 'translation.y': 5285644.0, 'translation.z': 0.0, 'rotation.x': 0.0, 'rotation.y': 0.0, 'rotation.z': 0.0, 'rotation.w': 1.0, 'frame_id': 'map', 'child_frame_id': 'map_gyor_0'}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='zala0_tf_publisher',
            output='screen',
            arguments=['639770.0', '5195040.0', '0.0','0', '0', '0', '1','map','map_zala_0'],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_gps_tf_publisher',
            output='screen',
            arguments=['0.0', '0.0', '0.1', '0.0', '0', '0', namespace + '/' + 'gps', namespace + '/' + 'base_link'], # TODO
        ),
    ])