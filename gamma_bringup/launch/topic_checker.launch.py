import launch
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='gamma_bringup',
            executable='topic_checker',
            name='topic_checker',
            parameters=[
                {
                    'topics_and_types': [
                        'gamma1/sensing/lidar/concatenated/pointcloud', 'sensor_msgs/msg/PointCloud2',
                        'ground', 'sensor_msgs/msg/PointCloud2',
                        'clustered_marker', 'visualization_msgs/msg/MarkerArray',
                        'gamma1/gps/duro/hea/current_pose', 'geometry_msgs/msg/PoseStamped',
                        'gamma1/gps/duro/ref/current_pose', 'geometry_msgs/msg/PoseStamped',
                        'gamma1/gps/duro/hea/status_string', 'std_msgs/msg/String',
                        'waypointarray', 'geometry_msgs/msg/PoseArray',
                        'targetpoints', 'geometry_msgs/msg/PoseArray',
                        'obstacle_avoidance_pose_array_topic', 'geometry_msgs/msg/PoseArray',
                        'pursuitspeedtarget', 'std_msgs/msg/Float32',
                        'cmd_vel', 'geometry_msgs/msg/Twist',
                        'crio_Twist', 'geometry_msgs/msg/Twist',
                        'ctrl_cmd', 'crio_msgs/msg/CrioMessage'
                    ]
                }
            ]
        )
    ])
