# jkk_utils
(Mostly) ROS 2 utility nodes and packages.

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5)](https://docs.ros.org/en/humble/)

# Usage

``` bash
cd ~/ros2_ws/src
```

``` bash
git clone https://github.com/jkk-research/jkk_utils
```

``` bash
cd ~/ros2_ws
```

``` bash
colcon build --packages-select drone_bringup time_utils gamma_bringup mcap_rec timing_benchmark gui_teleop
```

``` bash
source ~/ros2_ws/install/setup.bash
```


# Packages
- `drone_bringup`: ROS 2 package for drone drivers and settings
- `gamma_bringup`: ROS 2 package for Gamma Komondor drivers and settings
- `time_utils`: ROS 2 package for simple functions as human readable display, difference etc 
- `pose_repub`: Pose republisher in different format
- `mcap_rec`: Handy mcap recorder with presets
- `timing_benchmark`: Measure time delays in ROS 2
- `gui_teleop`: GUI for teleoperation and visualization 
- `demo_jkk`: Various demonstration related launch files and nodes

# Related
- https://github.com/jkk-research/docker_ros2_images
- https://github.com/szenergy/szenergy-public-resources/wiki/ROS-2-humble-jeston-docker