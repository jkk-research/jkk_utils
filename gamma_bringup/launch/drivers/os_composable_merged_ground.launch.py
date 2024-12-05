from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction

from launch.substitutions import LaunchConfiguration, FindExecutable
# from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    """
    Generate launch description for running ouster_ros components in a single
    process/container.
    """
    NAMESPACE = "gamma1"

    pkg_dir = get_package_share_directory('gamma_bringup')
    params_file_path = Path(pkg_dir) / 'launch' / 'drivers' / 'ouster_config_b.yaml'
    merger_params_file_path = Path(pkg_dir) / 'launch' / 'drivers' / 'ouster_config_comp_b.yaml'


    params_file = LaunchConfiguration('params_file')
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=str(params_file_path),
        description='Ouster driver parameters.'
    )

    merger_params_file = LaunchConfiguration('merger_params_file')
    merger_params_file_arg = DeclareLaunchArgument(
        'merger_params_file',
        default_value=str(merger_params_file_path),
        description='Ouster PCL Merger parameters.'
    )

    ouster_ns = LaunchConfiguration(NAMESPACE)
    ouster_ns_arg = DeclareLaunchArgument(
        'ouster_ns', default_value='gamma1')


    os_left_sensor = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterSensor',
        name='os_driver',
        namespace='gamma1/os_left',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_left_cloud = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterCloud',
        name='os_cloud',
        namespace='gamma1/os_left',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_right_sensor = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterSensor',
        name='os_driver',
        namespace='gamma1/os_right',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_right_cloud = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterCloud',
        name='os_cloud',
        namespace='gamma1/os_right',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_center_sensor = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterSensor',
        name='os_driver',
        namespace='gamma1/os_center',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_center_cloud = ComposableNode(
        package='ouster_ros',
        plugin='ouster_ros::OusterCloud',
        name='os_cloud',
        namespace='gamma1/os_center',
        parameters=[params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    os_pcl_merger = ComposableNode(
        package='gamma_bringup',
        plugin='merger::OusterPCLMerger',
        # executable from `rclcpp_components_register_node` (CMakeLists.txt)
        name='os_pcl_merger_node',
        namespace='gamma1',
        parameters=[merger_params_file],
        extra_arguments=[{'use_intra_process_comms': True}],
    )

    simple_z_filter = ComposableNode(
        package='arj_simple_perception',
        plugin='LidarFilterSimple',
        name='lidar_filter_simple_param_composable',
        namespace='lidar_filter_ns',
        extra_arguments=[{'use_intra_process_comms': True}],
        parameters=[
            {'cloud_topic': "/gamma1/sensing/lidar/concatenated/pointcloud"},
            {'cloud_frame': "/gamma1/TMF"},
            {'minX': 2.0},
            {'minY': -50.0},
            {'minZ': -2.5},
            {'maxX': 50.0},
            {'maxY': 50.0},
            {'maxZ': 5.0},
            {'use_sim_time': False},
        ],
    )

    ground_segment = ComposableNode(
        package='patchworkpp',
        plugin='patchworkpp::PatchworkppPointXYZI',
        name='ground_segmentation',
        # namespace='lexus3/os_left',
        parameters=[
               
                #{'cloud_topic': "lidar_filter_ns/lidar_filter_output"}, # Input pointcloud
                {'cloud_topic': "/gamma1/sensing/lidar/concatenated/pointcloud"},
                {'frame_id': "gamma1/TMF"},
                {'sensor_height': 2.6},
                {'num_iter': 3},             # Number of iterations for ground plane estimation using PCA.
                {'num_lpr': 20},             # Maximum number of points to be selected as lowest points representative.
                {'num_min_pts': 0},          # Minimum number of points to be estimated as ground plane in each patch.
                {'th_seeds': 1.0},           # threshold for lowest point representatives using in initial seeds selection of ground points.
                {'th_dist': 0.325},          # threshold for thickenss of ground.
                {'th_seeds_v': 0.25},        # threshold for lowest point representatives using in initial seeds selection of vertical structural points.
                {'th_dist_v': 0.9},          # threshold for thickenss of vertical structure.
                {'max_r': 80.0},             # max_range of ground estimation area
                {'min_r': 2.0},              # min_range of ground estimation area
                {'adaptive_seed_selection_margin':2.6},
                {'RNR_ver_angle_thr': -45.0},
                {'uprightness_thr': 0.101},  # threshold of uprightness using in Ground Likelihood Estimation(GLE). Please refer paper for more information about GLE.
                {'verbose': False},          # display verbose info
                {'display_time': False},     # display running_time and pointcloud sizes
                {'num_zones':4},
            ],
        extra_arguments=[{'use_intra_process_comms': True}],
    
    )

    euclidean_grid = ComposableNode(
            package='lidar_cluster',
            plugin='EuclideanGrid',
            name='euclidean_grid_filter_composable_unique',
            #namespace='euclidean_grid_filter_ns',
            extra_arguments=[{'use_intra_process_comms': True}],
            parameters=[
            {'points_in_topic': 'nonground',
            'points_out_topic': 'clustered_points',
            'marker_out_topic': 'clustered_marker',
            'tolerance': 1.0,
            'max_cluster_size': 4000,
            'voxel_leaf_size': 2.0,
            'min_points_number_per_voxel': 5,
            'verbose1': False,
            'verbose2': False,}
            ],
            )

    os_container = ComposableNodeContainer(
        name='os_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[
            os_left_sensor,
            os_left_cloud,
            os_right_sensor,
            os_right_cloud,
            os_center_sensor,
            os_center_cloud,
            os_pcl_merger,
            #simple_z_filter,
            ground_segment,
            euclidean_grid,

        ],
        output='screen',
        arguments=['--ros-args', '--log-level', 'INFO'],
    )


    def invoke_lifecycle_cmd(node_name, verb):
        ros2_exec = FindExecutable(name='ros2')
        return ExecuteProcess(
            cmd=[[ros2_exec, ' lifecycle set /', node_name, ' ', verb]],
            shell=True
        )

    sensor_left_configure_cmd = invoke_lifecycle_cmd('gamma1/os_left/os_driver', 'configure')
    sensor_left_activate_cmd = invoke_lifecycle_cmd('gamma1/os_left/os_driver', 'activate')
    sensor_right_configure_cmd = invoke_lifecycle_cmd('gamma1/os_right/os_driver', 'configure')
    sensor_right_activate_cmd = invoke_lifecycle_cmd('gamma1/os_right/os_driver', 'activate')
    sensor_center_configure_cmd = invoke_lifecycle_cmd('gamma1/os_center/os_driver', 'configure')
    sensor_center_activate_cmd = invoke_lifecycle_cmd('gamma1/os_center/os_driver', 'activate')
    

    return LaunchDescription([
        params_file_arg,
        merger_params_file_arg,
        ouster_ns_arg,
        os_container,
        TimerAction(period=4.0, actions=[sensor_left_configure_cmd]),
        TimerAction(period=8.0, actions=[sensor_left_activate_cmd]),
        TimerAction(period=12.0, actions=[sensor_right_configure_cmd]),
        TimerAction(period=16.0, actions=[sensor_right_activate_cmd]),
        TimerAction(period=20.0, actions=[sensor_center_configure_cmd]),
        TimerAction(period=24.0, actions=[sensor_center_activate_cmd]),
    ])
