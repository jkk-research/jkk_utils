#!/bin/bash

# START


screen -ls | grep foxglove_bridge


if ! screen -ls | grep -q "foxglove_bridge"; then
    echo -e "\e[42mStart foxglove_bridge\e[0m"
    screen -m -d -S foxglove_bridge bash -c 'source ~/ros2_ws/install/setup.bash && ros2 run foxglove_bridge foxglove_bridge --ros-args -p send_buffer_limit:=1048576'
else
    echo -e "\e[41merror\e[0m foxglove_bridge already started"
fi