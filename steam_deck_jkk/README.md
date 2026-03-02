# `steam_deck_jkk` ROS 2 package
Measure time delays in `ROS 2` `Humble`

[![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5)](https://docs.ros.org/en/humble/)

<img src="img/steamdeck01.svg" alt="Steam Deck" width="400"/>

## Build this `ROS 2` package

In the following `~/ros2_ws` is assumed as the ROS 2 workspace:

``` bash
cd ~/ros2_ws/src
```

``` bash
git clone https://github.com/jkk-research/jkk_utils
```

``` bash
cd ~/ros2_ws/
```

``` bash
colcon build --symlink-install --packages-select steam_deck_jkk
```

# Further 

- [github.com/szenergy/szenergy-public-resources/wiki/ROS-2---Steam-Deck](https://github.com/szenergy/szenergy-public-resources/wiki/ROS-2---Steam-Deck)