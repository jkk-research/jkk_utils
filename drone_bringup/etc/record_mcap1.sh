#!/bin/bash

## ROS 2 rosbag recorder (MCAP format)

cd /bag
mkdir -p $(date -I)
cd $(date -I)
TEXT1="$1"
VEH1="_drone1_"
TIME1="$(date +"%Y-%m-%d_%H-%M")"
FILE1="$TEXT1$VEH1$TIME1"
FILE2="x_rosparam_dump_$TEXT1$TIME1.txt"
PWD1="$(pwd)"
echo "Writing to file: $PWD1/$FILE1"
# 524288000 byte is ~0.5 GB
# 1048576000 byte is ~ 1 GB
ros2 bag record -s mcap -o $FILE1 --max-cache-size 1048576000 --storage-config-file mcap_writer_options1.yaml /drone1/gps/duro/current_pose /drone1/gps/duro/imu /drone1/gps/duro/mag /drone1/gps/duro/navsatfix /drone1/gps/duro/status_flag /drone1/gps/duro/status_string /drone1/gps/duro/time_ref /drone1/os/points /tf /tf_static

 

