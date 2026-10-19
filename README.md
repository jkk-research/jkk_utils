<h1 align="center">jkk_utils</h1>

<p align="center">
  <b>(Mostly) ROS 2 utility nodes and packages.</b>
</p>

<p align="center">
  <img alt="ROS 2: Humble" src="https://img.shields.io/badge/ros2-humble-34aec5?style=flat-square&logo=ros">
  <img alt="ROS 2: Jazzy" src="https://img.shields.io/badge/ros2-jazzy-34aec5?style=flat-square&logo=ros">
  <img alt="mcap: File" src="https://img.shields.io/badge/mcap-file-24d48b?style=flat-square">
  <a href="https://github.com/jkk-research/jkk_utils/blob/ros2/LICENSE">
    <img alt="License: GPLv3" src="https://img.shields.io/badge/License-GPLv3-red?style=flat-square">
  </a>
</p>

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
- `workspace_health`: GUI listing the git status (OK, Behind, Modified, Diverged...) of the GitHub repos in a workspace
- `demo_jkk`: Various demonstration related launch files and nodes

# Other directories
- `mcap_scripts`: Data manipulation scripts for mcap

# Images

<p align="center">
  <img src="workspace_health/resource/ws_health01.png" alt="rec_gui" width="600">
</p>

<p align="center">
  <img src="steam_deck_jkk/img/steamdeck01.svg" alt="steamdeck" width="600">
</p>


# Related
- https://github.com/jkk-research/docker_ros2_images
- https://github.com/szenergy/szenergy-public-resources/wiki/ROS-2-humble-jeston-docker
