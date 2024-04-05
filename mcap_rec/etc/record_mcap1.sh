#!/usr/bin/env bash

## ROS 2 rosbag recorder (MCAP format)

DIR1="$(pwd)"
DIR2=~/ros2_ws/src/jkk_utils/mcap_rec/etc/
cd /mnt/bag
DIR3=$(date -I)_bosch # eg. 2025-08-25_bosch
mkdir -p $DIR3
cd $DIR3
VEH1="_lexus3_"
TEXT1="$1" # first argument is the text
TIME1="$2"  # second argument is the time
FILE1="${TEXT1}${VEH1}${TIME1}"
PWD1="$(pwd)"
echo "Writing to file: $PWD1/$FILE1"
# 524288000 byte is ~0.5 GB
# 1048576000 byte is ~ 1 GB
TOPICS_FILE=$DIR2/preset_bosch01.txt
TOPICS="$(cat $TOPICS_FILE)"
ros2 bag record -s mcap -o $FILE1 --max-cache-size 1048576000 --storage-config-file $DIR2/mcap_writer_options1.yaml /lexus3/gps/duro/current_pose /lexus3/gps/duro/imu /lexus3/gps/duro/mag /lexus3/gps/duro/navsatfix /lexus3/gps/duro/status_flag /lexus3/gps/duro/status_string /lexus3/gps/duro/time_diff /lexus3/gps/duro/time_ref /lexus3/os_center/points /lexus3/os_left/points /lexus3/os_right/points /lexus3/zed2i/zed_node/left/image_rect_color/compressed /tf /tf_static

