import rclpy
from rclpy.node import Node
import std_msgs.msg as std_msg
import sensor_msgs.msg as sen_msg
from datetime import datetime # print in ISO format

class DiplayTimeSub(Node):

    def __init__(self):
        super().__init__('disptime')
        self.declare_parameter('topic', '/drone1/gps/duro/time_ref')
        my_topic = self.get_parameter('topic').get_parameter_value().string_value
        self.get_logger().info('Subscribing to %s' % my_topic)
        self.subscription = self.create_subscription(sen_msg.TimeReference, my_topic, self.timeref_callback, 10)
        self.subscription  # prevent unused variable warning

    def timeref_callback(self, msg):
        # convert nanosec to sec
        time_ros_frame = msg.header.stamp.sec + (msg.header.stamp.nanosec) / 1000000000
        time_duro_ref = msg.time_ref.sec + (msg.time_ref.nanosec) / 1000000000
        # time difference between the time_ref header and the time_ref field
        self.get_logger().info('%8.3f [%s]' % (time_ros_frame - time_duro_ref, datetime.utcfromtimestamp(time_ros_frame).isoformat().replace('T', ' ')))


def main(args=None):
    rclpy.init(args=args)
    display_time_sub = DiplayTimeSub()
    rclpy.spin(display_time_sub)
    display_time_sub.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()