# Reading from a MCAP file
# sudo apt install ros-$ROS_DISTRO-ros-base ros-$ROS_DISTRO-ros2bag ros-$ROS_DISTRO-rosbag2-transport ros-$ROS_DISTRO-rosbag2-storage-mcap 
import matplotlib.pyplot as plt
import numpy as np
from mcap import __version__

print(__version__)


"""script that reads ROS2 messages from an MCAP bag using the rosbag2_py API."""
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import rosbag2_py


def read_messages(input_bag: str):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=input_bag, storage_id="mcap"), rosbag2_py.ConverterOptions(input_serialization_format="cdr", output_serialization_format="cdr" ),)

    topic_types = reader.get_all_topics_and_types()

    def typename(topic_name):
        for topic_type in topic_types:
            if topic_type.name == topic_name:
                return topic_type.type
        raise ValueError(f"topic {topic_name} not in bag")

    while reader.has_next():
        topic, data, timestamp = reader.read_next()
        try:
            msg_type = get_message(typename(topic))
            msg = deserialize_message(data, msg_type)
            yield topic, msg, timestamp
        except Exception as e:
            #print(f"failed to deserialize message on topic {topic}: {e}") #TODO: fix this
            topic, data, timestamp = reader.read_next()
    del reader

def quaternion_to_euler_angle_vectorized1(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = np.where(t2>+1.0,+1.0,t2)
    #t2 = +1.0 if t2 > +1.0 else t2

    t2 = np.where(t2<-1.0, -1.0, t2)
    #t2 = -1.0 if t2 < -1.0 else t2
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return X, Y, Z 

inputs = []

# list all *.mcap in /mnt/c/Users/he/Downloads
directory = "/mnt/c/Users/he/Downloads"
import os
for filename in os.listdir(directory):
    if filename.endswith(".mcap"):
        #print(os.path.join(directory, filename))
        inputs.append(os.path.join(directory, filename))
    else:
        continue

# mcap_file1 = "ego_5_1_4_lexus3_2024-04-12_09-45_0.mcap"
# mcap_file1 = "ego_5_1_15_lexus3_2024-04-12_10-43_0.mcap"


# inputs.append(os.path.join(directory, mcap_file1))


i = 0
first_run = True
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

for input in inputs:
    print("opening: " + input)
    # plt.title('Vehicle Odometry\n' + input)
    # x = []
    # y = []
    # time = []
    pose_arr1 = np.empty((0,4))
    pose_arr2 = np.empty((0,4))
    pose_arr3 = np.empty((0,4))
    speed_arr1 = np.empty((0,2))
    for topic, msg, timestamp in read_messages(input):
        if(first_run):
            timestamp_start = timestamp
            first_run = False
        if (i % 1 == 0): # resample if necessary, 1 is no resampling
            if(topic == "/nissan9/vehicle_speed"):
                speed_data = msg.data
                speed_time = (timestamp) / 1000000000 ## convert to seconds
                speed_arr1 = np.append(speed_arr1,[[speed_time, speed_data]], axis=0)
            if(topic == "/lexus3/gps/duro/current_pose"):
                # x.append(msg.pose.position.x)
                # y.append(msg.pose.position.y)
                # time.append(msg.header.stamp.sec)
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                # quaterinion to euler
                quat1 = msg.pose.orientation
                orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                pose_arr1 = np.append(pose_arr1,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)
            if(topic == "/nissan9/gps/duro/current_pose"):
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                quat1 = msg.pose.orientation
                orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                pose_arr2 = np.append(pose_arr2,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)
    # plt.plot(x, y, label=input)

    # pose_arr1 = np.array([time, x, y])
    # print(pose_arr1)
    if pose_arr1.size != 0:
        save_path_pose_arr1 = input[:-5]  + "_posearr.csv"
        print("saved to: %s size: %d" % (save_path_pose_arr1, pose_arr1.shape[0]))
        np.savetxt(save_path_pose_arr1, pose_arr1, delimiter=',', fmt='%f', header='time,x,y,yaw') # 
        pose_arr1 = np.empty((0,4))
    if pose_arr2.size != 0:
        save_path_pose_arr2 = input[:-5]  + "_posearr2.csv"
        print("saved to: %s size: %d" % (save_path_pose_arr2, pose_arr2.shape[0]))
        np.savetxt(save_path_pose_arr2, pose_arr2, delimiter=',', fmt='%f', header='time,x,y,yaw') # 
        pose_arr2 = np.empty((0,4))    
    if speed_arr1.size != 0:
        save_path_speed_arr1 = input[:-5]  + "_speedarr.csv"
        print("saved to: %s size: %d" % (save_path_speed_arr1, speed_arr1.shape[0]))
        np.savetxt(save_path_speed_arr1, speed_arr1, delimiter=',', fmt='%f', header='time,speed') #
        speed_arr1 = np.empty((0,2))

# plt.legend()
# plt.show()