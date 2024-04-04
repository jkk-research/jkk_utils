# MCAP record preset for Bosch measurement 

import launch
import datetime

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, LogInfo, OpaqueFunction

DeclareLaunchArgument("tag", description="a tag to the recorded file", default_value="bosch01"),
tag_ = (LaunchConfiguration("tag"))


def exit_process_function(_launch_context):
    # ~/mcap/mcap info /mnt/bag/2024-04-04_bosch/scenario01_lexus3_2024-04-04_17-00/scenario01_lexus3_2024-04-04_17-00_0.mcap 
    print("Recording finished.")
    # tag_ to string
    tag_ = _launch_context.launch_configurations["tag"]
    print("")
    print("ros2 bag info /mnt/bag/" + get_date() + "_bosch/"+ tag_ +"_lexus3_" + get_date_and_time() + ".mcap")
    print("~/mcap/mcap info /mnt/bag/" + get_date() + "_bosch/"+ tag_ +"_lexus3_" + get_date_and_time() + "/" + tag_ +"_lexus3_" + get_date_and_time() + "_0.mcap")

def get_date_and_time():
    """Get the current date and time."""
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')

def get_date():
    """Get the current date."""
    return datetime.datetime.now().strftime('%Y-%m-%d')

def generate_launch_description():
    
    return LaunchDescription([
        ExecuteProcess(
            cmd=['/home/dev/ros2_ws/src/jkk_utils/mcap_rec/etc/record_mcap1.sh', tag_, get_date_and_time()],
            log_cmd=True,
            shell=True,
            output='screen',
            # sigterm_timeout='0',
            # sigkill_timeout='0',
            on_exit=[
                OpaqueFunction(
                    function=exit_process_function
                ),
                # LogInfo(msg='This message prints properly.')
            ]
        )
    ])
