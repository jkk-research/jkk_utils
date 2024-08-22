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
            name='MF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '5.103', # TODO: @rudolfkrecht
                '--y',  '0.0',
                '--z',  '1.35',
                '--yaw', '0.0', # TODO: better in roll, pitch, yaw?
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'MF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='LF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '5.0',
                '--y',  '1.1',
                '--z',  '0.701',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'LF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='RF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '5.0',
                '--y',  '-1.1',
                '--z',  '0.701',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'RF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='LM_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '3.448',
                '--y',  '1.1',
                '--z',  '1.088',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'LM'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='RM_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '3.448',
                '--y',  '-1.1',
                '--z',  '1.088',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'RM'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TMF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '3.150',
                '--y',  '0.0',
                '--z',  '2.301',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TMF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TLF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '2.9',
                '--y',  '0.73',
                '--z',  '2.150',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TLF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TRF_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '2.9',
                '--y',  '-0.73',
                '--z',  '2.150',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TRF'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TLR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.5',
                '--y',  '0.73',
                '--z',  '2.150',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TLR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TRR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.5',
                '--y',  '-0.73',
                '--z',  '2.150',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TRR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TLS_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '2.163',
                '--y',  '1.14',
                '--z',  '2.206',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TLS'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='TRS_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '2.163',
                '--y',  '-1.14',
                '--z',  '2.206',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TRS'
            ],
        ),
    ])