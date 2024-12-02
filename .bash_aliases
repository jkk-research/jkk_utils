# some more ls aliases for JKK, Szenergy and friends
# https://github.com/jkk-research/jkk_utils/edit/ros2/.bash_aliases
# cd ~; rm .bash_aliases; wget https://raw.githubusercontent.com/jkk-research/jkk_utils/ros2/.bash_aliases
alias r2='source ~/ros2_ws/install/setup.bash && echo -e "  \e[34msource\e[0m \e[33m~/ros2_ws\e[0m/install/setup.bash"'
alias aw='source ~/autoware/install/setup.bash && echo -e "  \e[34msource\e[0m \e[33m~/autoware\e[0m/install/setup.bash"'
alias f1='source ~/f1tenth_ws/install/setup.bash && echo -e "  \e[34msource\e[0m \e[33m~/f1tenth_ws\e[0m/install/setup.bash"'
alias r1='screen -mdS roscore1 bash -c 'roscore' && echo "screen roscore1"'
# wheeltec robot
alias start_drivers='~/ros2_ws/src/drivers/shell/start_drivers.sh && echo -e " "'
alias start_lane='~/ros2_ws/src/lane_following_cam/shell/start_lane.sh && echo -e " "'
alias stop_all='~/ros2_ws/src/lane_following_cam/shell/stop_all.sh && echo -e " "'
