from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from math import pi, degrees, radians

def generate_launch_description():
    DeclareLaunchArgument("map", description="a lanelet process", default_value="gyor1"),
    ## possible values: gyor1, gyor2, zala_uni, zala_motorway, zala_city
    return LaunchDescription([
        ## TODO: choose based on LaunchConfiguration("map")
        Node(
            package='lanelet2_rviz2',
            executable='visualize_osm',
            output='screen',
            parameters=[
                {"frame_id": "map_gyor_0"},
                {"line_width": 1.0},
                {"osm_filename": "/home/dev/autoware_map/gyor_uni.osm"},
                {"center_map": False},
                {"speed_color_max": 90.0},
            ],
        ),       
        Node(
            package='pcd_publisher',
            executable='pcd_publisher',
            output='screen',
            parameters=[
                {"pcd_file_path": "/mnt/bag/dlio_map2.pcd"},
                {"frame_id": "map_gyor_0"},
                {"topic_name": "map"}, # https://github.com/rsasaki0109/lidar_localization_ros2
                {"rate": 1},
                {"x_translation": -24.0},
                {"y_translation": 77.0},
                {"z_translation": 0.0},
                {"x_rotation": 0.0},
                {"y_rotation": 0.0},
                {"z_rotation": radians(-177.1)}, # -177.1 deg is -3.09097 rad
            ],
        ),
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
    ])