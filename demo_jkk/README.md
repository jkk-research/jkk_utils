# `demo_jkk` `ROS 2` package
ROS 2 demo launch files

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5)](https://docs.ros.org/en/humble/)

```
sudo apt install ros-humble-rviz-2d-overlay-plugins
```
or https://github.com/jkk-research/rviz_2d_overlay_plugins

https://github.com/astuff/pacmod3#installation

## Run 

``` bash
ros2 run demo_jkk odometry_from_twist --ros-args -p status_topic:=/lexus3/vehicle_status -p wheelbase:=2.789
```

``` bash
ros2 run demo_jkk odometry_from_twist --ros-args -p status_topic:=/nissan9/vehicle_status -p wheelbase:=2.7
```


``` bash
ros2 launch demo_jkk odometry_from_twist.launch.py 
```

