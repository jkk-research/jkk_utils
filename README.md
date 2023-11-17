# jkk_utils
(Mostly) ROS 2 utility nodes and packages.

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-blue)](https://docs.ros.org/en/humble/)

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
colcon build --packages-select drone_bringup time_utils
```

``` bash
source ~/ros2_ws/install/setup.bash
```


# Packages
- `drone_bingup`: ROS 2 package for drone drivers and settings
- `time_utils`: ROS 2 package for simple functions as human readable display, difference etc 

# Related
- https://github.com/jkk-research/docker_ros2_images
- https://github.com/szenergy/szenergy-public-resources/wiki/ROS-2-humble-jeston-docker