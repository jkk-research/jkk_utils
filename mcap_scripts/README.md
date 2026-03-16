# `mcap_scripts` directory

Some handy `MCAP` scripts for data manipulation.

![Static Badge](https://img.shields.io/badge/mcap-File-24d48b?style=flat-square)

## Operating System

Tested on: 
- Windows 11 (Python 3.12)
- Ubuntu 22.04 (Python 3.12)

> [!CAUTION]
> MCAP is ROS 2 agnostic, and can be used in any Python project, but `rosbag2-api` **does rely**  on ROS2. Use `mcap-ros2-support` which is not dependent on ROS 2.

`Python MCAP ROS2 support` package (`mcap-ros2-support`) provides ROS2 support for the Python MCAP file format reader. It has no dependencies on ROS2 itself or a ROS 2 environment, and can be used in any Python project.

## Installation

``` bash
pip install mcap mcap-ros2-support matplotlib numpy pandas scipy
```

## Links
- https://mcap.dev/guides/cli
- https://github.com/foxglove/mcap/releases
- https://github.com/jkk-research/jkk-research.github.io/blob/master/notebooks/mcap_to_trajectory.ipynb
- https://pypi.org/project/mcap-ros2-support/ (recommended, no ROS 2 dependency)
- https://pypi.org/project/rosbag2-api/ (ROS 2 dependency)