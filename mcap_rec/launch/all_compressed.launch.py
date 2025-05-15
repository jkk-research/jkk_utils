# MCAP record all topic, but compressed

import os
import datetime

from launch import LaunchDescription
from launch.actions import ExecuteProcess, OpaqueFunction
from launch.actions import TimerAction
from ament_index_python.packages import get_package_share_directory



# get the current package path
# package path should look similar: ~/ros2_ws/install/mcap_rec/share/mcap_rec/
package_path = get_package_share_directory("mcap_rec")
# get the current path (pwd)
current_path = os.getcwd()

cmd1 = package_path + "/etc/record_mcap1.sh"

# print("package_path: ", package_path)
# print("current_path: ", current_path)
# print("cmd1: ", cmd1)


def exit_process_function(_launch_context):
    print("Recording finished.")
    # tag_ to string
    print("")
    print("")
    print("ros2 bag info " + current_path + "/" + date_and_time_)
    print("~/mcap/mcap info " + current_path + "/" + date_and_time_ + "/" + date_and_time_ + "_0.mcap")

def get_date_and_time():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')

def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

date_and_time_ = get_date_and_time()
date_ = get_date()

def generate_launch_description():
    
    return LaunchDescription([
        ExecuteProcess(
            cmd=[cmd1, date_and_time_],
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
        ), 
        # # static tf
        # TimerAction(
        # period=2.0, # delay
        # actions=[    
        #     IncludeLaunchDescription(
        #         PythonLaunchDescriptionSource([
        #             FindPackageShare("lexus_bringup"), '/launch', '/tf_static.launch.py'])
        #     ),
        # ]),
    ])



