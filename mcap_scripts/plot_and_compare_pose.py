## This script is runnable on Windows, and works (with slight modification) on Ubuntu and MacOS
## This script is used to read the mcap file and print the messages of the topics
## Similar functionality to compare_pose_foxglove.ts (type script for Foxglove Studio)
## https://github.com/jkk-research/jkk_utils/blob/ros2/mcap_scripts/compare_pose_foxglove.ts


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
from scipy.spatial.transform import Rotation as R

def pose_to_matrix(pose):
    position = pose.pose.position
    orientation = pose.pose.orientation
    rotation = R.from_quat([
        orientation.x,
        orientation.y,
        orientation.z,
        orientation.w
    ]).as_matrix()
    trans_mat = np.eye(4)
    trans_mat[:3, :3] = rotation
    trans_mat[:3, 3] = [position.x, position.y, position.z]
    return trans_mat

def matrix_to_pose(matrix: np.ndarray, pose):
    translation = matrix[:3, 3]
    rotation = R.from_matrix(matrix[:3, :3]).as_quat()
    pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = translation
    pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z, pose.pose.orientation.w = rotation
    return pose

def calculate_relative_pose(ndt, gps):
    ndt_mat = pose_to_matrix(ndt)
    gps_mat = pose_to_matrix(gps)

    relative_mat = np.linalg.inv(ndt_mat) @ gps_mat
    template_pose = ndt  # Use the NDT pose as a template for the output
    template_pose.pose.position.x = 0.0
    template_pose.pose.position.y = 0.0
    template_pose.pose.position.z = 0.0
    template_pose.pose.orientation.x = 0.0
    template_pose.pose.orientation.y = 0.0
    template_pose.pose.orientation.z = 0.0
    template_pose.pose.orientation.w = 1.0
    return matrix_to_pose(relative_mat, template_pose)

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
        pose_diff = []
        for schema, channel, message, ros_msg in reader.iter_decoded_messages():
            if channel.topic == "/localization/pose_estimator/pose":
                # print("%s -- %d || %d.%d" % (channel.topic, message.log_time, ros_msg.header.stamp.sec, ros_msg.header.stamp.nanosec))
                # print("NDT position: ", ros_msg.pose.position.x, ros_msg.pose.position.y, ros_msg.pose.position.z)
                # print("NDT orientation: ", ros_msg.pose.orientation.x, ros_msg.pose.orientation.y, ros_msg.pose.orientation.z, ros_msg.pose.orientation.w)
                pose_ndtr.append(ros_msg)
                pose_diff.append(ros_msg)  # Initialize pose_diff with NDT poses
            if channel.topic == "/lexus3/gps/nova/current_pose":
                # print("%s -- %d || %d.%d" % (channel.topic, message.log_time, ros_msg.header.stamp.sec, ros_msg.header.stamp.nanosec))
                # print("GNSS position: ", ros_msg.pose.position.x, ros_msg.pose.position.y, ros_msg.pose.position.z)
                # print("GNSS orientation: ", ros_msg.pose.orientation.x, ros_msg.pose.orientation.y, ros_msg.pose.orientation.z, ros_msg.pose.orientation.w)
                pose_gnss.append(ros_msg)

        # Debugging offset for visualization
        for p in pose_ndtr:
            p.pose.position.x = p.pose.position.x +10.0 
        
        gnss_relative_poses = pose_gnss

        timestamp_ndtr = [p.header.stamp.sec + p.header.stamp.nanosec * 1e-9 for p in pose_ndtr]
        timestamp_gnss = [p.header.stamp.sec + p.header.stamp.nanosec * 1e-9 for p in pose_gnss]

        print(type(pose_gnss[0]))

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
        start = timestamp_gnss[0]
        for i, tn in enumerate(timestamp_ndtr):
            for j, tg in enumerate(timestamp_gnss):
                # Find the closest NDT pose in time
                if abs(tg -tn) < 0.1:
                    # print(f"{i}:  NDT pose at {tn-start:.2f}s GNSS pose at {tg-start:.2f}s matches")

                    # Calculate the difference in position
                    pose_diff[i].pose.position.x = pose_ndtr[i].pose.position.x - pose_gnss[j].pose.position.x
                    pose_diff[i].pose.position.y = pose_ndtr[i].pose.position.y - pose_gnss[j].pose.position.y
                    
                    # pose_diff[i] = calculate_relative_pose(pose_ndtr[i], pose_gnss[j])

                    break

        print("Number of GNSS poses:", len(pose_gnss))
        print("Number of NDT poses:", len(pose_ndtr))
        fig, axs = plt.subplots(1, 2, figsize=(16, 8))

        # Plot 1: GNSS Pose Relative to NDT Frame
        axs[0].plot(0, 0, 'bo', label='NDT Reference (0,0)')
        axs[0].plot(
            [p.pose.position.x for p in pose_diff],
            [p.pose.position.y for p in pose_diff],
            'r.', label='GNSS Poses'
        )
        axs[0].set_xlabel('X Position (m)')
        axs[0].set_ylabel('Y Position (m)')
        axs[0].set_title('GNSS Pose Relative to NDT Frame')
        axs[0].axis('equal')
        axs[0].legend()
        axs[0].grid(True)

        # Plot 2: GNSS Pose and NDT Pose (original positions)
        # TODO: why does this not work?
        # axs[1].plot(
        #     [p.pose.position.x for p in pose_ndtr],
        #     [p.pose.position.y for p in pose_ndtr],
        #     'bo', label='NDT Pose'
        # )
        axs[1].plot(
            [p.pose.position.x for p in pose_gnss],
            [p.pose.position.y for p in pose_gnss],
            'r.', label='GNSS Pose'
        )
        axs[1].set_xlabel('X Position (m)')
        axs[1].set_ylabel('Y Position (m)')
        axs[1].set_title('GNSS Pose and NDT Pose')
        axs[1].axis('equal')
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        plt.show()





if __name__ == "__main__":
    main()