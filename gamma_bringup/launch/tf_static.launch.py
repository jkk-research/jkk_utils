from launch import LaunchDescription
from launch_ros.actions import Node
import math

def generate_launch_description():

    ns_vehicle = "gamma1"

    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='gyor0_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '697237.0',
                '--y',  '5285644.0',
                '--z',  '0.0',
                '--qx', '0.0',
                '--qy', '0.0',
                '--qz', '0.0',
                '--qw', '1.0',

                '--frame-id',      'map',
                '--child-frame-id','map_gyor_0'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='zala0_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '639770.0',
                '--y',  '5195040.0',
                '--z',  '0.0',
                '--qx', '0.0',
                '--qy', '0.0',
                '--qz', '0.0',
                '--qw', '1.0',

                '--frame-id',       'map',
                '--child-frame-id', 'map_zala_0'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='duro_gps_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.6', # TODO: @rudolfkrecht
                '--y',  '0.0',
                '--z',  '0.2',
                '--qx', '0.0', # TODO: better in roll, pitch, yaw?
                '--qy', '0.0',
                '--qz', '0.0',
                '--qw', '1.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'duro_gps'
            ],
        ),
    ])