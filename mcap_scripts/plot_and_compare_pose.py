## This script is runnable on Windows, and works (with slight modification) on Ubuntu and MacOS
## This script is used to read the mcap file and print the messages of the topics

# pip install mcap mcap-ros2-support matplotlib numpy pandas
# mcap-ros2-support works on Windows too!

# /lexus3/gps/nova/current_pose	        geometry_msgs/msg/PoseStamped (GNSS)
# /localization/pose_estimator/pose	    geometry_msgs/msg/PoseStamped (NDT reference)
# /tf	                                tf2_msgs/msg/TFMessage
# /tf_static	                        tf2_msgs/msg/TFMessage


import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from mcap_ros2.decoder import DecoderFactory
from mcap.reader import make_reader
from scipy.spatial import cKDTree


def main():
    file_name = '/mnt/c/bag/test03_gps_ndt_compare_0.mcap'
    # file_name = 'C:\\bag\\test03_gps_ndt_compare_0.mcap'
    with open(file_name, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        #list all topics and types
        channels = reader.get_summary().channels.items()
        print("Available topics are the following:")
        for index, (channel_key, channel_value) in enumerate(channels):
            print("%2d. topic: %s" % (index+1, channel_value.topic))
        print("")

        pose_gnss = []
        pose_ndtr = []
        for schema, channel, message, ros_msg in reader.iter_decoded_messages():
            if channel.topic == "/localization/pose_estimator/pose":
                # print("%s -- %d || %d.%d" % (channel.topic, message.log_time, ros_msg.header.stamp.sec, ros_msg.header.stamp.nanosec))
                # print("NDT position: ", ros_msg.pose.position.x, ros_msg.pose.position.y, ros_msg.pose.position.z)
                # print("NDT orientation: ", ros_msg.pose.orientation.x, ros_msg.pose.orientation.y, ros_msg.pose.orientation.z, ros_msg.pose.orientation.w)
                pose_ndtr.append(ros_msg)
            if channel.topic == "/lexus3/gps/nova/current_pose":
                # print("%s -- %d || %d.%d" % (channel.topic, message.log_time, ros_msg.header.stamp.sec, ros_msg.header.stamp.nanosec))
                # print("GNSS position: ", ros_msg.pose.position.x, ros_msg.pose.position.y, ros_msg.pose.position.z)
                # print("GNSS orientation: ", ros_msg.pose.orientation.x, ros_msg.pose.orientation.y, ros_msg.pose.orientation.z, ros_msg.pose.orientation.w)
                pose_gnss.append(ros_msg)

        gnss_relative_poses = pose_gnss

        timestamp_ndtr = [p.header.stamp.sec + p.header.stamp.nanosec * 1e-9 for p in pose_ndtr]
        timestamp_gnss = [p.header.stamp.sec + p.header.stamp.nanosec * 1e-9 for p in pose_gnss]


        # plt.figure(figsize=(10, 10))
        # plt.plot(timestamp_gnss)
        # plt.plot(timestamp_ndtr)
        # plt.xlabel('Index')
        # plt.ylabel('Timestamp (s)')
        # plt.title('Timestamps of GNSS and NDT Poses')
        # plt.legend(['GNSS Poses', 'NDT Poses'])
        # plt.grid(True)
        # plt.show()

        current_time = 0.0
        pose_diff = pose_ndtr
        start = timestamp_gnss[0]
        for i, tn in enumerate(timestamp_ndtr):
            for j, tg in enumerate(timestamp_gnss):
                # Find the closest NDT pose in time
                if abs(tg -tn) < 0.1:
                    # print(f"{i}:  NDT pose at {tn-start:.2f}s GNSS pose at {tg-start:.2f}s matches")

                    # Calculate the difference in position
                    pose_diff[i].pose.position.x = pose_ndtr[i].pose.position.x - pose_gnss[j].pose.position.x
                    pose_diff[i].pose.position.y = pose_ndtr[i].pose.position.y - pose_gnss[j].pose.position.y
                    
                    # TODO: transform ndt to gnss frame instead of subtracting position difference

                    break

        print("Number of GNSS poses:", len(pose_gnss))
        print("Number of NDT poses:", len(pose_ndtr))

        plt.plot(0, 0, 'bo', label='NDT Reference (0,0)')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.title('GNSS Pose Relative to NDT Frame')
        plt.plot(
            [p.pose.position.x for p in pose_diff],
            [p.pose.position.y for p in pose_diff],
            'ro', label='GNSS Poses'
        )
        plt.axis('equal')
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    main()