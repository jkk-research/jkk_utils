#!/bin/bash

# START


screen -ls | grep joy1


if ! screen -ls | grep -q "joy1"; then
    echo -e "\e[42mStart joy1\e[0m"
    screen -m -d -S joy1 bash -c 'source ~/ros2_ws/install/setup.bash && ros2 launch steam_deck_jkk joy1.launch.py'
else
    echo -e "\e[41merror\e[0m joy1 already started"
fi