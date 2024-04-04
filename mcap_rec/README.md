# `mcap_rec` ROS 2 package
Handy presets for MCAP record `ROS 2` `Humble`

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5)](https://docs.ros.org/en/humble/)


## Build this `ROS 2` package

In the following `~/ros2_ws` is assumed as the ROS 2 workspace:

``` bash
cd ~/ros2_ws/src
```

``` bash
clone
```

``` bash
cd ~/ros2_ws/
```

``` bash
colcon build --symlink-install --packages-select mcap_rec
```

## Run `ROS 2` node / launch file

``` bash
source ~/ros2_ws/install/setup.bash
```

``` bash
ros2 launch mcap_rec preset_bosch01.launch.py tag:=scenario01
```


## Links
- https://mcap.dev/guides/cli
- https://github.com/foxglove/mcap/releases

## Useful
``` bash
wget https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.42/mcap-linux-amd64 -o mcap
```