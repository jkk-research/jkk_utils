#!/bin/bash

## ROS 2 rosbag recorder (MCAP format)

cd /bag
mkdir -p $(date -I)
cd $(date -I)
TEXT1="$1"
TIME1="$(date +"%Y-%m-%d_%H-%M")"
FILE1="$TEXT1_drone1_$TIME1"
FILE2="x_rosparam_dump_$TEXT1$TIME1.txt"
PWD1="$(pwd)"
echo "Writing to file: $PWD1/$FILE1"
# 524288000 byte is ~0.5 GB
ros2 bag record -s mcap --all -o $FILE1 --max-cache-size 524288000


