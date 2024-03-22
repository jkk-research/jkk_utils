from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

def generate_launch_description():
    return LaunchDescription([
        # Drivers
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch/drivers', '/gps_duro_reference.launch.py'])
        ),
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch/drivers', '/can_pacmod3.launch.xml'])
        ),
        # General nodes
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/tf_static.launch.py'])
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/3d_marker.launch.py'])
        ),
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource([
                FindPackageShare("lexus_bringup"), '/launch', '/foxglove_bridge_launch.xml'])
        ),
        TimerAction(
            period=2.0, # delay
            actions=[
                Node(
                    package='lexus_bringup',
                    executable='path_steering_and_kmph',
                    name='path_steering_and_kmph_d',
                    output='screen',
                    parameters=[
                        {
                        "marker_color": "p", 
                        "path_size": 550,
                        "publish_kmph": True,
                        "pose_topic": "lexus3/current_pose",
                        "pose_frame": "lexus3/base_link",
                        }
                    ]
                ), 
            ]),
        TimerAction(
            period=3.0, # delay
            actions=[
                Node(
                    package='wayp_plan_tools',
                    executable='waypoint_saver',
                    name='wayp_saver',
                    output='screen',
                    parameters=[
                        {"tf_child_frame_id": "lexus3/base_link"},
                        {"file_dir": "/mnt/bag/waypoints/"},
                        #{"file_name": "gyor1.csv"},
                        {"file_name": "gyor4eto.csv"},
                        #{"file_name": "zala01uni.csv"},
                        #{"file_name": "zala03uniteljeskor.csv"},
                        #{"file_name": "zala04smartteljeskor.csv"},
                        #{"file_name": "zala08_demokor.csv"},
                        #{"file_name": "zala06_teljes_kor.csv"},
                        #{"file_name": "gyor02fek.csv"},
                    ],
                )     
            ]),    

    ])
