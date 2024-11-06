#!/usr/bin/env python
# Roughly based on the algorithm of Lucas Walter
# https://github.com/lucasw/transform_point_cloud
# transform a pointcloud into a new frame

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time
import tf2_ros
from tf2_ros import TransformException, LookupException, ExtrapolationException
# import copy
from threading import Lock
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2 as pc2
import numpy as np
from scipy.spatial.transform import Rotation

class TransformPointCloud(Node):
    def __init__(self):
        super().__init__('transform_point_cloud')
        self.lock = Lock()
        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=12))
        self.tl = tf2_ros.TransformListener(self.tf_buffer, self)
        self.sub = self.create_subscription(PointCloud2, "/lexus3/os_center/points", self.point_cloud_callback, 2)
        self.pub = self.create_publisher(PointCloud2, "/map_points", 2)
        self.cloud_in = None
        self.lidar_frame = "lexus3/os_center_a_laser_data_frame" # source_frame
        self.map_frame = "map_gyor_0" # target_frame
        self.timeout = 0.5
        self.offset_lookup_time = +0 ## offset in seconds
        self.based_on_message_time = True ## True: based on message time, False: based on current time
        print("TransformPointCloud started")

    def point_cloud_callback(self, msg):

        current_time = self.get_clock().now()
        # print("point_cloud_callback")
        msg_time = Time.from_msg(msg.header.stamp)
        diff_time = current_time - msg_time
        print("  ROStime: " + str(current_time.seconds_nanoseconds()[0]) + "." + str(current_time.seconds_nanoseconds()[1])[:3] + " MSG time: " + str(msg.header.stamp.sec) + "." + str(msg.header.stamp.nanosec)[:3])
        print("  Time diff: " + str(diff_time.to_msg().sec) + "." + str(diff_time.to_msg().nanosec)[:3])
        self.publish_point_cloud(msg, msg.header.stamp)
        with self.lock:
            self.cloud_in = msg

    def publish_point_cloud(self, cloud_in, stamp):
        if self.based_on_message_time:
            lookup_time = stamp ## based on message time
        else: ## based on current time 
            lookup_time = self.get_clock().now() ## based on current time
        lookup_time.sec += self.offset_lookup_time ## time with offset
        # self.map_frame = cloud_in.header.frame_id
        trans = None
        try:
            time0 = Time()
            # trans = self.tf_buffer.lookup_transform(self.map_frame, self.lidar_frame, lookup_time, Duration(seconds=self.timeout))
            trans = self.tf_buffer.lookup_transform(self.map_frame, self.lidar_frame, time0, Duration(seconds=self.timeout))
        except Exception as ex:
            print("Exception: " + str(ex))
        if trans is not None:
            # transform the point cloud
            t = np.eye(4)
            q = trans.transform.rotation
            x = trans.transform.translation
            t[:3, :3] = Rotation.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
            t[:3, 3] = [x.x, x.y, x.z]

            points = list(pc2.read_points(cloud_in, field_names=("x", "y", "z"), skip_nans=True)) # despite skip_nans = True, it still returns NaNs
            # filter out (nan, nan, nan) points
            points = [p for p in points if not np.isnan(p[0]) and not np.isnan(p[1]) and not np.isnan(p[2])]
            points_map = np.ones((len(points), 4), dtype=np.float32)
            print("  Points: " + str(points[500]))

            # TODO: 
            # points_map[:, :3] = np.array(points, dtype=np.float32)
            # points_map = np.dot(t, points_map.T).T


            fields = [
                PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            ]
            
            pcl_map_header = cloud_in.header
            pcl_map_header.frame_id = self.map_frame
            cloud_out_map = pc2.create_cloud(pcl_map_header, fields, points_map[:, :3])
            self.pub.publish(cloud_out_map)
        else:
            print("Skip!!!\n\n")


def main(args=None):
    rclpy.init(args=args)
    transform_point_cloud = TransformPointCloud()
    rclpy.spin(transform_point_cloud)
    transform_point_cloud.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()