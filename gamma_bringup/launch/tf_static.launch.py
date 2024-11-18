from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import math
import os

def generate_launch_description():

    ns_vehicle = "gamma1"
    urdf_file = os.path.join(get_package_share_directory('gamma_bringup'), 'urdf', 'gamma.urdf')

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
                '--x',  '5.234',
                '--y',  '0.0',
                '--z',  '1.083',
                '--yaw', '0.0',
                '--pitch', '0.603884',
                '--roll', '3.141592',

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
                '--y',  '1.105',
                '--z',  '0.701',
                '--yaw', '0.96', 
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
                '--y',  '-1.0',
                '--z',  '0.701',
                '--yaw', '-0.94', 
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
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='SML_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.56',
                '--y',  '1.2',
                '--z',  '0.586',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'SML'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='SMR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.56',
                '--y',  '-1.2',
                '--z',  '0.586',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'SMR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='LR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '-1.029',
                '--y',  '1.08',
                '--z',  '0.92',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'LR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='RR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '-1.029',
                '--y',  '-1.08',
                '--z',  '0.92',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'RR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='MR_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '-1.313',
                '--y',  '0.0',
                '--z',  '0.539',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'MR'
            ],
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='duro_gps_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '1.58',
                '--y',  '0.775',
                '--z',  '2.46',
                '--qx', '0.0',
                '--qy', '0.0',
                '--qz', '0.0',
                '--qw', '1.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'TRR'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_gps_tf_publisher',
            output='screen',
            # https://raw.githubusercontent.com/wiki/szenergy/szenergy-public-resources/img/2022.L.01.svg
            # TODO
            arguments=[
                '--x',     '-2.86', ## Based on Novatel Application Suite By default, INS position is reported at the centre of the IMU. (Set to IMU)
                '--y',     '-0.775',
                '--z',     '-2.46.',
                '--yaw',   '0.0',
                '--pitch', '0.0',
                '--roll',  '0.0',

                '--frame-id',       ns_vehicle + '/' + 'gps',
                '--child-frame-id', ns_vehicle + '/' + 'base_link'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='MF_united_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '5.234',
                '--y',  '0.0',
                '--z',  '1.083',
                '--yaw', '0.0', 
                '--pitch', '0.0',
                '--roll', '0.0',

                '--frame-id',       ns_vehicle + '/' + 'base_link',
                '--child-frame-id', ns_vehicle + '/' + 'MF_united'
            ],
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description':open(urdf_file).read()}]
        ),
    ])