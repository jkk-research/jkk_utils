from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    DeclareLaunchArgument("map", description="a lanelet process", default_value="gyor1"),
    ## possible values: gyor1, gyor2, zala_uni, zala_motorway, zala_city
    return LaunchDescription([
        Node(
            package='lanelet2_rviz2',
            executable='visualize_osm',
            output='screen',
            parameters=[
                {"frame_id": "map_gyor_0"},
                {"line_width": 1.0},
            ],
        ),
        ## TODO: choose based on LaunchConfiguration("map")
        ExecuteProcess(
            cmd=[
                'ros2', 'topic', 'pub', '/osm_filename', 
                'std_msgs/msg/String', 
                "{data: '/home/dev/autoware_map/gyor_uni.osm'}"
            ],
            output='screen'
        ),
        # Node(
        #     package='pcl_ros',
        #     executable='pcd_to_pointcloud',
        #     name='pcd_to_pointcloud',
        #     parameters=[
        #         {'file_name': '/home/he/dlio_map2.pcd'},
        #         {'tf_frame': 'map_gyor_0'},
        #         {'publishing_period_ms': 1000},
        #     ],
        # ),
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