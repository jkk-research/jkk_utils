from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    sim_wp_pkg_name = 'sim_wayp_plan_tools'
    sim_wp_pkg_dir = get_package_share_directory(sim_wp_pkg_name)
    #print(sim_wp_pkg_dir)

    return LaunchDescription([
        Node(
            package='wayp_plan_tools',
            executable='waypoint_loader_with_stops',
            name='wayp_load',
            output='screen',
            parameters=[
                {"file_dir": sim_wp_pkg_dir + "/csv"},
                #{"file_dir": "/mnt/bag/waypoints/"},
                {"file_name": "sim_waypoints3.csv"},
                {"per_waypoint_display": 5}, # display speed every 5th waypoint 
            ],
        )
    ])