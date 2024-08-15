## This script is runnable on Windows, and works (with slight modification) on Ubuntu and MacOS
## This script is used to read the mcap file and print the messages of the topics

# pip install mcap mcap-ros2-support matplotlib numpy pandas scipy
# mcap-ros2-support works on Windows too!


import matplotlib.pyplot as plt
import numpy as np
from mcap import __version__
from scipy import interpolate
import sys
from pathlib import Path

print(__version__)

from mcap_ros2.decoder import DecoderFactory
from mcap.reader import make_reader



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

def main():
    inputs = []

    # list all *.mcap in /mnt/c/Users/he/Downloads
    # directory = "/mnt/c/Users/he/Downloads"
    directory = Path(sys.argv[1]) # "C:/database/DT_SZE/1_meres/1_beallas/h1"
    import os
    for filename in os.listdir(directory):
        if filename.endswith(".mcap"):
            #print(os.path.join(directory, filename))
            inputs.append(os.path.join(directory, filename))
        else:
            continue
    i = 0
    ts = 0.05
    firstLoop = True
    measurementReliable = True #novatel GPS used

    #step 1: calculate t0 and t1
    t0 = 0
    t1 = 0
    t = 0
    for input in inputs:
        with open(input, "rb") as f: 
                reader = make_reader(f, decoder_factories=[DecoderFactory()])
                #iterate over all messages
                for schema, channel, message, msg in reader.iter_decoded_messages():
                    if(channel.topic == "/nissan9/vehicle_speed"):
                        t = (message.log_time) / 1000000000 ## convert to seconds

                    if(channel.topic == "/lexus3/gps/nova/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                    elif(channel.topic == "/lexus3/gps/duro/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        measurementReliable = False

                    if(channel.topic == "/lexus3/gps/nova/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                    elif(channel.topic == "/lexus3/gps/duro/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        measurementReliable = False

                    if(channel.topic == "/nissan9/gps/nova/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                    elif(channel.topic == "/nissan9/gps/duro/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        measurementReliable = False

                    if(channel.topic == "/nissan9/gps/nova/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                    elif(channel.topic == "/nissan9/gps/duro/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        measurementReliable = False

                    if(channel.topic == "/golf/vectornav/current_pose"):
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


    i_a = 0
    first_run = True
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    for input in inputs:
        print("opening: " + input)
        pose_arr1 = np.empty((0,4))
        pose_arr2 = np.empty((0,4))
        pose_arr3 = np.empty((0,4))
        cov_arr1 = np.empty((0,4))
        cov_arr2 = np.empty((0,4))
        cov_arr3 = np.empty((0,4)) 
        speed_arr1 = np.empty((0,2)) # ego - Lexus
        speed_arr2 = np.empty((0,2)) # target 1 - Leaf
        speed_arr3 = np.empty((0,2)) # target 2 - Golf

        t = 0
        
        with open(input, "rb") as f:
            reader = make_reader(f, decoder_factories=[DecoderFactory()])
            #iterate over all messages
            for schema, channel, message, msg in reader.iter_decoded_messages():
                if(first_run):
                    timestamp_start = message.log_time
                    first_run = False
                if (i_a % 1 == 0): # resample if necessary, 1 is no resampling
                    # ego - Lexus signals
                    if(channel.topic == "/lexus3/vehicle_speed_kmph"):
                        t = message.log_time / 1000000000 ## convert to seconds
                        speed_arr1 = np.append(speed_arr1,[[t, msg.data/3.6]], axis=0)

                    if(channel.topic == "/lexus3/gps/nova/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        quat1 = msg.pose.orientation
                        orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                        x = msg.pose.position.x
                        y = msg.pose.position.y
                        pose_arr1 = np.append(pose_arr1,[[t, x, y, orientation1_yaw]], axis=0)
                    elif(channel.topic == "/lexus3/gps/duro/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        quat1 = msg.pose.orientation
                        orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                        x = msg.pose.position.x
                        y = msg.pose.position.y
                        pose_arr1 = np.append(pose_arr1,[[t, x, y, orientation1_yaw]], axis=0)

                    if(channel.topic == "/lexus3/gps/nova/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        cov1 = msg.position_covariance[0]
                        cov2 = msg.position_covariance[4]
                        cov3 = msg.position_covariance[8]
                        cov_arr1 = np.append(cov_arr1,  [[t,cov1,cov2,cov3]], axis=0)
                    elif(channel.topic == "/lexus3/gps/duro/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        cov1 = msg.position_covariance[0]
                        cov2 = msg.position_covariance[4]
                        cov3 = msg.position_covariance[8]
                        cov_arr1 = np.append(cov_arr1,  [[t,cov1,cov2,cov3]], axis=0)

                    # target 1 - leaf signals
                    if(channel.topic == "/nissan9/vehicle_speed"):
                        t = message.log_time / 1000000000 ## convert to seconds
                        speed_arr2 = np.append(speed_arr2,[[t, msg.data]], axis=0)

                    if(channel.topic == "/nissan9/gps/nova/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        cov1 = msg.position_covariance[0]
                        cov2 = msg.position_covariance[4]
                        cov3 = msg.position_covariance[8]
                        cov_arr2 = np.append(cov_arr2,  [[t,cov1,cov2,cov3]], axis=0)
                    elif(channel.topic == "/nissan9/gps/duro/navsatfix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        cov1 = msg.position_covariance[0]
                        cov2 = msg.position_covariance[4]
                        cov3 = msg.position_covariance[8]
                        cov_arr2 = np.append(cov_arr2,  [[t,cov1,cov2,cov3]], axis=0)

                    if(channel.topic == "/nissan9/gps/nova/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        quat1 = msg.pose.orientation
                        orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                        pose_arr2 = np.append(pose_arr2,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)
                    elif(channel.topic == "/nissan9/gps/duro/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        quat1 = msg.pose.orientation
                        orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                        pose_arr2 = np.append(pose_arr2,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)

                    # target 2 - golf signals
                    # NOTE: vehicle speed signal is not measured at target 2!
                    if(channel.topic == "/golf/vectornav/fix"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        cov1 = msg.position_covariance[0]
                        cov2 = msg.position_covariance[4]
                        cov3 = msg.position_covariance[8]
                        cov_arr3 = np.append(cov_arr3,  [[t,cov1,cov2,cov3]], axis=0)
                    if(channel.topic == "/golf/vectornav/current_pose"):
                        t = msg.header.stamp.sec + msg.header.stamp.nanosec / 1000000000
                        quat1 = msg.pose.orientation
                        orientation1_roll, orientation1_pitch, orientation1_yaw = quaternion_to_euler_angle_vectorized1(quat1.w, quat1.x, quat1.y, quat1.z)
                        pose_arr3 = np.append(pose_arr3,[[t, msg.pose.position.x, msg.pose.position.y, orientation1_yaw]], axis=0)

                i_a += 1
        pos_arr1_interp = np.empty((0,4))
        pos_arr2_interp = np.empty((0,4))
        pos_arr3_interp = np.empty((0,4))
        cov_arr1_interp = np.empty((0,4))
        cov_arr2_interp = np.empty((0,4))
        cov_arr3_interp = np.empty((0,4))
        speed_arr1_interp = np.empty((0,2))
        speed_arr2_interp = np.empty((0,2))
        speed_arr3_interp = np.empty((0,2))

        # ego - Lexus signal interpolation
        if pose_arr1.size != 0:
            f1 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 1], axis=0, bounds_error=False, fill_value=0)
            f2 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 2], axis=0, bounds_error=False, fill_value=0)
            f3 = interpolate.interp1d(pose_arr1[:,0], pose_arr1[:, 3], axis=0, bounds_error=False, fill_value=0)

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
        if speed_arr1.size != 0:
            f1 = interpolate.interp1d(speed_arr1[:,0], speed_arr1[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
            for t in time:
                speed_arr1_interp = np.append(speed_arr1_interp, [[t,f1(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = speed_arr1_interp
                headers = headers + "time_ego, speed_ego"
            else:
                arr = np.append(arr, speed_arr1_interp, axis=-1)
                headers = headers + ", time_ego, speed_ego"

            speed_arr1 = np.empty((0,2))
            speed_arr1_interp = np.empty((0,2))

        # target 1 - leaf signal interpolation    
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
        if speed_arr2.size != 0:
            f1 = interpolate.interp1d(speed_arr2[:,0], speed_arr2[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
            for t in time:
                speed_arr2_interp = np.append(speed_arr2_interp, [[t,f1(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = speed_arr2_interp
                headers = headers + "time_target1, speed_target1"
            else:
                arr = np.append(arr, speed_arr2_interp, axis=-1)
                headers = headers + ", time_target1, speed_target1"

            speed_arr2 = np.empty((0,2))
            speed_arr2_interp = np.empty((0,2))
        if cov_arr2.size != 0:
            f1 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
            f2 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,2], axis=0, bounds_error=False, fill_value="extrapolate")
            f3 = interpolate.interp1d(cov_arr2[:,0], cov_arr2[:,3], axis=0, bounds_error=False, fill_value="extrapolate")
            
            for t in time:
                cov_arr2_interp = np.append(cov_arr2_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = cov_arr2_interp
                headers = headers + "time_target1, covxx_target1, covyy_target1, covzz_target1"
            else:
                arr = np.append(arr, cov_arr2_interp, axis=-1)
                headers = headers + ", time_target1, covxx_target1, covyy_target1, covzz_target1"

            cov_arr2 = np.empty((0,4))
            cov_arr2_interp = np.empty((0,4))

        # target 2 - golf signal interpolation
        if pose_arr3.size != 0:
            f1 = interpolate.interp1d(pose_arr3[:,0], pose_arr3[:, 1], axis=0, bounds_error=False, fill_value="extrapolate")
            f2 = interpolate.interp1d(pose_arr3[:,0], pose_arr3[:, 2], axis=0, bounds_error=False, fill_value="extrapolate")
            f3 = interpolate.interp1d(pose_arr3[:,0], pose_arr3[:, 3], axis=0, bounds_error=False, fill_value="extrapolate")

            for t in time:
                pos_arr3_interp = np.append(pos_arr3_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = pos_arr3_interp
                headers = headers + "time_target2, x_target2, y_target2, yaw_target2"
            else:
                arr = np.append(arr, pos_arr3_interp, axis=-1)
                headers = headers + ", time_target2, x_target2, y_target2, yaw_target2"

            pose_arr3 = np.empty((0,4))
            pos_arr3_interp = np.empty((0,4))
        if cov_arr3.size != 0:
            f1 = interpolate.interp1d(cov_arr3[:,0], cov_arr3[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
            f2 = interpolate.interp1d(cov_arr3[:,0], cov_arr3[:,2], axis=0, bounds_error=False, fill_value="extrapolate")
            f3 = interpolate.interp1d(cov_arr3[:,0], cov_arr3[:,3], axis=0, bounds_error=False, fill_value="extrapolate")
            
            for t in time:
                cov_arr3_interp = np.append(cov_arr3_interp, [[t,f1(t), f2(t), f3(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = cov_arr3_interp
                headers = headers + "time_target2, covxx_target2, covyy_target2, covzz_target2"
            else:
                arr = np.append(arr, cov_arr3_interp, axis=-1)
                headers = headers + ", time_target2, covxx_target2, covyy_target2, covzz_target2"

            cov_arr3 = np.empty((0,4))
            cov_arr3_interp = np.empty((0,4))
        if speed_arr3.size != 0:
            f1 = interpolate.interp1d(speed_arr3[:,0], speed_arr3[:,1], axis=0, bounds_error=False, fill_value="extrapolate")
            for t in time:
                speed_arr3_interp = np.append(speed_arr3_interp, [[t,f1(t)]], axis=0)
            
            if(firstLoop):
                firstLoop = False
                arr = speed_arr3_interp
                headers = headers + "time_target2, speed_target2"
            else:
                arr = np.append(arr, speed_arr3_interp, axis=-1)
                headers = headers + ", time_target2, speed_target2"

            speed_arr3 = np.empty((0,2))
            speed_arr3_interp = np.empty((0,2))

    print(arr.shape)
    if (arr.size!=0):
        if (measurementReliable):
            save_path_arr = os.path.join(directory, "mergedData.csv")
        else:
            save_path_arr = os.path.join(directory, "mergedDataUnreliableGPS.csv")
        print("saved to: %s size: %d %d" % (save_path_arr, arr.shape[0], arr.shape[1]))
        np.savetxt(save_path_arr, arr, delimiter=',', fmt='%f', header=headers) #

if __name__ == "__main__":
    main()