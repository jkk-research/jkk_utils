## This script is runnable on Windows, and works (with slight modification) on Ubuntu and MacOS
## This script is used to read the mcap file and print the messages of the topics

# pip install mcap mcap-ros2-support matplotlib numpy pandas
# mcap-ros2-support works on Windows too!


# import matplotlib.pyplot as plt
# import numpy as np
# from mcap import __version__
# print(__version__)

from mcap_ros2.decoder import DecoderFactory
from mcap.reader import make_reader


def main():
    with open('C:\\Users\\he\\Downloads\\t1_nissan_scenario_5_1_6_2024-04-12_09-52_0.mcap', "rb") as f:
    # with open('/mnt/c/bag/lexus3-2024-04-05-gyor.mcap', "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        #list all topics and types
        channels = reader.get_summary().channels.items()
        print("Available topics are the following:")
        for index, (channel_key, channel_value) in enumerate(channels):
            print("%2d. topic: %s" % (index+1, channel_value.topic))
        print("")


        #iterate over all messages
        i = 0
        for schema, channel, message, ros_msg in reader.iter_decoded_messages():
            if (i % 1000 == 0): #print every 1000th message
                if schema.name == "sensor_msgs/msg/Imu":
                    # print(f"{channel.topic} {schema.name} [{message.log_time}]: {ros_msg}")
                    print("%s -- %d || %s" % (channel.topic, message.log_time, ros_msg.linear_acceleration.x))
                    # break
                if(channel.topic == "/lexus3/gps/duro/current_pose"):
                    print("%s -- %d || %s" % (channel.topic, message.log_time, ros_msg.pose.position.x))
                    # break
                if(channel.topic == "/nissan9/gps/duro/current_pose"):
                    print("%s -- %d || %s" % (channel.topic, message.log_time, ros_msg.pose.position.x))
                    # break
                if(channel.topic == "/tf"):
                    print("%s -- %d || %s" % (channel.topic, message.log_time, ros_msg.transforms[0].transform.translation.x))
                    # break
                # print(f"{channel.topic} {schema.name} [{message.log_time}]: {ros_msg}")
            i += 1


if __name__ == "__main__":
    main()