# jkk_utils
(Mostly) ROS 2 utility nodes and packages.

![Static Badge](https://img.shields.io/badge/ROS_2-Humble-34aec5?style=flat-square&logo=ros)
![Static Badge](https://img.shields.io/badge/ROS_2-Jazzy-34aec5?style=flat-square&logo=ros)
![Static Badge](https://img.shields.io/badge/mcap-File-24d48b?style=flat-square)
[![Static Badge](https://img.shields.io/badge/License-GPLv3-red?style=flat-square)](https://github.com/jkk-research/jkk_utils/blob/ros2/LICENSE)

#24d48b21
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
colcon build --packages-select drone_bringup time_utils gamma_bringup mcap_rec timing_benchmark gui_teleop steam_deck_jkk --symlink-install
```

``` bash
source ~/ros2_ws/install/setup.bash
```

## `bash_aliases`

[bash_aliases](https://github.com/jkk-research/jkk_utils/blob/ros2/.bash_aliases)


```bash
cd ~; rm .bash_aliases; wget https://raw.githubusercontent.com/jkk-research/jkk_utils/ros2/.bash_aliases; exec bash
```

## QoS overrides 

```bash
cd ~; wget https://raw.githubusercontent.com/jkk-research/jkk_utils/refs/heads/ros2/qos_tf.yaml
```

```bash
ros2 bag play /mnt/c/bag/lexus3-2024-04-05-gyor.mcap \
--clock --loop \
--qos-profile-overrides-path ~/qos_tf.yaml
```


# Packages
- `drone_bringup`: ROS 2 package for drone drivers and settings
- `gamma_bringup`: ROS 2 package for Gamma Komondor drivers and settings
- `time_utils`: ROS 2 package for simple functions as human readable display, difference etc 
- `pose_repub`: Pose republisher in different format
- `mcap_rec`: Handy mcap recorder with presets
- `timing_benchmark`: Measure time delays in ROS 2
- `steam_deck_jkk`: Steam Deck specific utilities
- `gui_teleop`: GUI for teleoperation and visualization 
- `demo_jkk`: Various demonstration related launch files and nodes

# Other directories
- `mcap_scripts`: Data manipulation scripts for mcap

# Related
- https://github.com/jkk-research/docker_ros2_images
- https://github.com/szenergy/szenergy-public-resources/wiki/ROS-2-humble-jeston-docker
