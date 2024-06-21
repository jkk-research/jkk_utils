# Reading from a MCAP file
# sudo apt install ros-$ROS_DISTRO-ros-base ros-$ROS_DISTRO-ros2bag ros-$ROS_DISTRO-rosbag2-transport ros-$ROS_DISTRO-rosbag2-storage-mcap 
import matplotlib.pyplot as plt
import numpy as np
from mcap import __version__
from scipy import interpolate

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
directory = "/home/gfigneczi1/DTTransformScripts/data/5_1_9"
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
ts = 0.05;
firstLoop = True

#step 1: calculate t0 and t1
t0 = 0
t1 = 0
t = 0
for input in inputs:
    for topic, msg, timestamp in read_messages(input):
        if(topic == "/nissan9/vehicle_speed"):
                t = (timestamp) / 1000000000 ## convert to seconds
        if(topic == "/lexus3/gps/duro/current_pose"):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
        if(topic == "/lexus3/gps/duro/navsatfix"):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
        if(topic == "/nissan9/gps/duro/navsatfix"):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
        if(topic == "/nissan9/gps/duro/current_pose"):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
        if (t0==0):
            t0 = t
            t1 = t
        else:
            t0 = min(t,t0)
            t1 = max(t,t1)

# resampling and interpolation: first production of the time channel
# searching for t0 (least time out of all) and last (highest time of all)
time = np.arange(t0,t1,ts)
print("t0=%.3f,t1=%.3f, lenght of measurement is %.3f secs" % (t0, t1, t1-t0))
print("interpolation with ts = %.3f secs" % (ts))

# step 2: getting data and interpolate
headers = ""

for input in inputs:
    print("opening: " + input)
    # plt.title('Vehicle Odometry\n' + input)
    # x = []
    # y = []
    # time = []
    pose_arr1 = np.empty((0,4))
    pose_arr2 = np.empty((0,4))
    pose_arr3 = np.empty((0,4))
    cov_arr1 = np.empty((0,4))
    cov_arr2 = np.empty((0,4))
    speed_arr1 = np.empty((0,2))

    t = 0

    for topic, msg, timestamp in read_messages(input):
            if(topic == "/nissan9/vehicle_speed"):
                t = (timestamp) / 1000000000 ## convert to seconds
                speed_arr1 = np.append(speed_arr1,[[t, msg.data]], axis=0)
            if(topic == "/lexus3/gps/duro/current_pose"):
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                quat1 = msg.pose.orientation
                orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                x = msg.pose.position.x
                y = msg.pose.position.y
                pose_arr1 = np.append(pose_arr1,[[t,  x,y,orientation1_yaw]], axis=0)
            if(topic == "/lexus3/gps/duro/navsatfix"):
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                cov1 = msg.position_covariance[0]
                cov2 = msg.position_covariance[4]
                cov3 = msg.position_covariance[8]
                cov_arr1 = np.append(cov_arr1,  [[t,cov1,cov2,cov3]], axis=0)
            if(topic == "/nissan9/gps/duro/navsatfix"):
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                cov1 = msg.position_covariance[0]
                cov2 = msg.position_covariance[4]
                cov3 = msg.position_covariance[8]
                cov_arr2 = np.append(cov_arr2,  [[t,cov1,cov2,cov3]], axis=0)
            if(topic == "/nissan9/gps/duro/current_pose"):
                t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                quat1 = msg.pose.orientation
                orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                pose_arr2 = np.append(pose_arr2,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)

    pos_arr1_interp = np.empty((0,4))
    pos_arr2_interp = np.empty((0,4))
    cov_arr1_interp = np.empty((0,4))
    cov_arr2_interp = np.empty((0,4))
    speed_arr_interp = np.empty((0,2))
    
    if pose_arr1.size != 0:
        save_path_pose_arr1 = input[:-5]  + "_posearr.csv"
        f1 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 1], axis=0, bounds_error=False, fill_value="extrapolate")
        f2 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 2], axis=0, bounds_error=False, fill_value="extrapolate")
        f3 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 3], axis=0, bounds_error=False, fill_value="extrapolate")

        for t in time:
            pos_arr1_interp = np.append(pos_arr1_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
        
        if(firstLoop):
            firstLoop = False
            arr = pos_arr1_interp
            headers = headers + "time_ego, x_ego, y_ego, yaw_ego"
        else:
            arr = np.append(arr, pos_arr1_interp, axis=-1)
            headers = headers + ", time_ego, x_ego, y_ego, yaw_ego"

        pose_arr1 = np.empty((0,4))
        pos_arr1_interp = np.empty((0,4))
    if pose_arr2.size != 0:
        f1 = interpolate.interp1d(pose_arr2[:,0], pose_arr2[:, 1], axis=0, bounds_error=False, fill_value="extrapolate")
        f2 = interpolate.interp1d(pose_arr2[:,0], pose_arr2[:, 2], axis=0, bounds_error=False, fill_value="extrapolate")
        f3 = interpolate.interp1d(pose_arr2[:,0], pose_arr2[:, 3], axis=0, bounds_error=False, fill_value="extrapolate")

        for t in time:
            pos_arr2_interp = np.append(pos_arr2_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)

        if(firstLoop):
            firstLoop = False
            arr = pos_arr2_interp
            headers = headers + "time_target1, x_target1, y_target1, yaw_target1"
        else:
            headers = headers + ", time_target1, x_target1, y_target1, yaw_target1"
            arr = np.append(arr, pos_arr2_interp, axis=-1)

        pose_arr2 = np.empty((0,4))   
        pos_arr2_interp = np.empty((0,4)) 
    if speed_arr1.size != 0:
        f1 = interpolate.interp1d(speed_arr1[:,0], speed_arr1[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
        for t in time:
            speed_arr_interp = np.append(speed_arr_interp, [[t,f1(t)]], axis=0)
        
        if(firstLoop):
            firstLoop = False
            arr = speed_arr_interp
            headers = headers + "time_target1, speed_target1"
        else:
            arr = np.append(arr, speed_arr_interp, axis=-1)
            headers = headers + ", time_target1, speed_target1"

        speed_arr1 = np.empty((0,2))
        speed_arr_interp = np.empty((0,2))
    if cov_arr1.size != 0:
        f1 = interpolate.interp1d(cov_arr1[:,0], cov_arr1[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
        f2 = interpolate.interp1d(cov_arr1[:,0], cov_arr1[:,2], axis=0, bounds_error=False, fill_value="extrapolate")
        f3 = interpolate.interp1d(cov_arr1[:,0], cov_arr1[:,3], axis=0, bounds_error=False, fill_value="extrapolate")
        
        for t in time:
            cov_arr1_interp = np.append(cov_arr1_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
        
        if(firstLoop):
            firstLoop = False
            arr = cov_arr1_interp
            headers = headers + "time_ego, covxx_ego, covyy_ego, covzz_ego"
        else:
            arr = np.append(arr, cov_arr1_interp, axis=-1)
            headers = headers + ", time_ego, covxx_ego, covyy_ego, covzz_ego"

        cov_arr1 = np.empty((0,4))
        cov_arr1_interp = np.empty((0,4))
    if cov_arr2.size != 0:
        f1 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
        f2 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,2], axis=0, bounds_error=False, fill_value="extrapolate")
        f3 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,3], axis=0, bounds_error=False, fill_value="extrapolate")
        
        for t in time:
            cov_arr2_interp = np.append(cov_arr2_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
        
        if(firstLoop):
            firstLoop = False
            arr = cov_arr2_interp
            headers = headers + "time_target, covxx_target, covyy_target, covzz_target"
        else:
            arr = np.append(arr, cov_arr2_interp, axis=-1)
            headers = headers + ", time_target, covxx_target, covyy_target, covzz_target"

        cov_arr2 = np.empty((0,4))
        cov_arr2_interp = np.empty((0,4))

print(arr.shape)
if (arr.size!=0):
    save_path_arr = os.path.join(directory, "mergedData.csv")
    print("saved to: %s size: %d %d" % (save_path_arr, arr.shape[0], arr.shape[1]))
    np.savetxt(save_path_arr, arr, delimiter=',', fmt='%f', header=headers) #

# plt.legend()
# plt.show()