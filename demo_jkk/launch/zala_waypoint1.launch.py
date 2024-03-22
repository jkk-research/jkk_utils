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
                    parameters=[{"marker_color": "b", "path_size": 550}]
                ), 
            ]),
        # Control nodes   
        TimerAction(
            period=2.0, # delay
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        FindPackageShare("lexus_bringup"), '/launch', '/speed_control.launch.py'])
                ),
            ]),     
        Node(
            package='wayp_plan_tools',
            executable='waypoint_loader',
            name='wayp_load',
            output='screen',
            parameters=[
                {"file_dir": "/mnt/bag/waypoints/"},
                #{"file_name": "gyor1.csv"},
                #{"file_name": "gyor4eto.csv"},
                #{"file_name": "zala02unitest.csv"},
                #{"file_name": "zala03uniteljeskor.csv"},
                #{"file_name": "zala06_teljes_kor.csv"},
                {"file_name": "zala08_demokor.csv"},
                #{"file_name": "zala01uni.csv"},
                #{"file_name": "gyor02fek.csv"},
            ],
        ),
        Node(
            package='wayp_plan_tools',
            executable='waypoint_to_target',
            name='wayp2target',
            output='screen',
            parameters=[
                {"lookahead_min": 11.0},
                {"lookahead_max": 17.0},
                {"mps_alpha": 3.5}, # 12.6
                {"mps_beta": 5.5}, # 19.8
                {"waypoint_topic": "lexus3/waypointarray"}
            ],
        ),
        TimerAction(
            period=3.0, # delay
            actions=[
                Node(
                    package='wayp_plan_tools',
                    executable='single_goal_pursuit',
                    name='single_goal_pursuit_1',
                    output='screen',
                    parameters=[
                        {"cmd_topic": "lexus3/cmd_vel"},
                        {"wheelbase": 2.789},
                        {"waypoint_topic": "lexus3/targetpoints"},
                    ],
                ),        
            ],
        ),    
        # TimerAction(
        #     period=3.0, # delay
        #     actions=[
        #         Node(
        #             package='wayp_plan_tools',
        #             executable='stanley_control',
        #             name='stanley',
        #             output='screen',
        #             parameters=[
        #                 {"cmd_topic": "lexus3/cmd_vel"},
        #                 {"wheelbase": 2.789},
        #                 {"waypoint_topic": "lexus3/targetpoints"},
        #                 {"cross_track_err_rate": 0.8},
        #                 {"heading_err_rate": 0.0},
        #             ],
        #         ),        
        #     ],
        # ),  

        # ros2 run rqt_reconfigure rqt_reconfigure 
        Node(
            package='rqt_reconfigure',
            executable='rqt_reconfigure',
            name='rqt_rec',
            #output='screen',
        ),
        Node(
            package='rviz_2d_overlay_plugins',
            executable='string_to_overlay_text',
            name='string_to_overlay_text_gps',
            output='screen',
            parameters=[
                {"string_topic": "/lexus3/gps/status_string"},
                {"fg_color": "b"}, # colors can be: r,g,b,w,k,p,y (red,green,blue,white,black,pink,yellow)
            ],
        ),
        Node(
            package='rviz_2d_overlay_plugins',
            executable='string_to_overlay_text',
            name='string_to_overlay_text_ctr_status',
            output='screen',
            parameters=[
                {"string_topic": "/lexus3/control_status"},
                {"fg_color": "r"}, # colors can be: r,g,b,w,k,p,y (red,green,blue,white,black,pink,yellow)
            ],
        ),        
        Node(
            package='gui_lexus',
            executable='pub_lane_markers',
            name='pub_lane_markers_1',
            output='screen',
        ),
    ])
