# `time_utils` package

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5)](https://docs.ros.org/en/humble/)

# Test topic pub

``` yaml
ros2 topic pub /drone1/gps/duro/time_ref sensor_msgs/msg/TimeReference "{header: {stamp: {sec: 1625246100, nanosec: 0}, frame_id: 'ros_time_frame'}, time_ref: {sec: 1625246099, nanosec: 1000000}, source: 'gps_duro'}"
```