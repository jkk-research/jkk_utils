from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([
        Node(
            package='pose_repub',
            executable='pub_gps',
            output='screen',
            parameters=[
                {"pose_topic": "/current_pose_fake_orientation"},
                {"frame_id": "map"},  
                {"child_frame_id": "base_link"},
                {"offset_x": -640123.88},
                {"offset_y": -5193659.53},
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='gyor0_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '0.466',
                '--y',  '0.0',
                '--z',  '0.849',
                '--qx', '0.0',
                '--qy', '0.0',
                '--qz', '0.0',
                '--qw', '1.0',
                '--frame-id',      'base_link',
                '--child-frame-id','laser_sensor_frame'
            ],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='gyor0_tf_publisher',
            output='screen',
            arguments=[
                '--x',  '0.0',
                '--y',  '0.0',
                '--z',  '0.0',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '1.5708',
                '--frame-id',      'laser_sensor_frame',
                '--child-frame-id','laser_data_frame'
            ],
        ),

    ])