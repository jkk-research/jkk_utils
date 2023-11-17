import rclpy
from rclpy.node import Node
import std_msgs.msg as std_msg
import sensor_msgs.msg as sen_msg
from datetime import datetime # print in ISO format

class DiplayTimeOnce(Node):

    def __init__(self):
        super().__init__('dispt')
        self.subscription = self.create_subscription(sen_msg.TimeReference, '/drone1/gps/duro/time_ref', self.timeref_callback, 10)
        self.subscription  # prevent unused variable warning

    def timeref_callback(self, msg):
        # convert nanosec to sec
        time_ros_frame = msg.header.stamp.sec + (msg.header.stamp.nanosec) / 1000000000
        time_duro_ref = msg.time_ref.sec + (msg.time_ref.nanosec) / 1000000000
        # time difference between the time_ref header and the time_ref field
        print('%.3f [%s]' % (time_ros_frame - time_duro_ref, datetime.utcfromtimestamp(time_ros_frame).isoformat().replace('T', ' ')))
        self.destroy_subscription(self.subscription)
        # self.destroy_node()
        # rclpy.shutdown()
        # return

def main(args=None):
    rclpy.init(args=args)
    display_time_once_sub = DiplayTimeOnce()
    rclpy.spin_once(display_time_once_sub)
    display_time_once_sub.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()