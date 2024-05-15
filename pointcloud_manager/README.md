# PointCloud Manager for ROS 2 - Humble
This repository is responsible for managing multiple pointclouds in real-time.

# Merging PCL
To merge pointclouds, just run `ros2 launch pointcloud_manager_launch.py`.

You only need to configure the parameters in `config/params.yaml`, where you need to give the *topics*, *frames*s, *child_frame*s in the proper format. *(You will see it in the default params.yaml file)*