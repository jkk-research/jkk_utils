from launch import LaunchDescription
from launch_ros.actions import Node

# ros2 run joy joy_node --ros-args -p dev:=/dev/input/by-id/usb-Valve_Software_Steam_Deck_Controller_MEDA33302CF4-if02-event-joystick -p deadzone:=0.1 -p autorepeat_rate:=20.0
# TODO: test

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            output='screen',
            parameters=[
                {
                    'dev': '/dev/input/by-id/usb-Valve_Software_Steam_Deck_Controller_MEDA33302CF4-if02-event-joystick'
                },
                {'deadzone': 0.1},
                {'autorepeat_rate': 20.0},
            ],
        ),
    ])
