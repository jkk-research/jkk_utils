// publishes nav_msgs/Path and steering marker and km/h

#include <iostream>
#include <vector>
#include <cmath>
#include "rclcpp/rclcpp.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "std_msgs/msg/float64.hpp"


using namespace std::chrono_literals;
using std::placeholders::_1;

class SteerMarkerNode : public rclcpp::Node
{
public:
    SteerMarkerNode() : Node("steering_node")
    {
        this->declare_parameter<std::string>("steer_topic", "/steering_angle");
        this->declare_parameter<std::string>("marker_topic", "steering_marker");
        // this->declare_parameter<std::string>("frame_id", "laser_data_frame");
        this->declare_parameter<std::string>("frame_id", "laser_sensor_frame");

        this->get_parameter("steer_topic", steer_topic);
        this->get_parameter("marker_topic", marker_topic);
        this->get_parameter("frame_id", frame_id);

        sub_steering = this->create_subscription<std_msgs::msg::Float64>(steer_topic, 10, std::bind(&SteerMarkerNode::vehicleSteerCallback, this, _1));
        marker_pub = this->create_publisher<visualization_msgs::msg::Marker>(marker_topic, 1);
        // Call loop function 20 Hz (50 milliseconds)
        // timer_ = this->create_wall_timer(std::chrono::milliseconds(50), std::bind(&SteerMarkerNode::loop, this));
        RCLCPP_INFO_STREAM(this->get_logger(), "Node started: " << this->get_name() << " subscribed: " << steer_topic << " publishing: " << marker_topic);
    }

private:
    void vehicleSteerCallback(const std_msgs::msg::Float64::SharedPtr steer_msg)
    {
        steering_angle = steer_msg->data * 1.8;
        RCLCPP_INFO_STREAM_ONCE(this->get_logger(), "Received steering angle. " << steering_angle);
        // RCLCPP_INFO_STREAM(this->get_logger(), "Received steering angle. " << steering_angle);
        visualization_msgs::msg::Marker steer_marker;
        steer_marker.header.frame_id = frame_id;
        steer_marker.header.stamp = this->now();
        steer_marker.ns = "steering_path";
        steer_marker.id = 0;
        steer_marker.type = steer_marker.LINE_STRIP;
        steer_marker.action = visualization_msgs::msg::Marker::MODIFY;
        steer_marker.pose.position.x = 0;
        steer_marker.pose.position.y = 0;
        steer_marker.pose.position.z = 0;
        steer_marker.pose.orientation.x = 0.0;
        steer_marker.pose.orientation.y = 0.0;
        steer_marker.pose.orientation.z = 0.0;
        steer_marker.pose.orientation.w = 1.0;
        steer_marker.scale.x = 0.6;
        // https://github.com/jkk-research/colors

        steer_marker.color.r = 0.30f;
        steer_marker.color.g = 0.69f;
        steer_marker.color.b = 0.31f;
        steer_marker.color.a = 1.0;
        steer_marker.lifetime = rclcpp::Duration::from_seconds(0);
        double marker_pos_x = 0.0, marker_pos_y = 0.0, theta = 0.0;
        for (int i = 0; i < 140; i++)
        {
            marker_pos_x += 0.01 * 10 * cos(theta);
            marker_pos_y += 0.01 * 10 * sin(theta);
            theta += 0.01 * 10 / wheelbase * tan(steering_angle);
            geometry_msgs::msg::Point p;
            p.x =  1 * marker_pos_x;
            p.y = -1 * marker_pos_y;
            steer_marker.points.push_back(p);
        }
        marker_pub->publish(steer_marker);
        steer_marker.points.clear();
    }

    // void loop()
    // {}
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_steering;
    std::string steer_topic, marker_topic, frame_id;
    const double wheelbase = 2.789;
    double steering_angle;
    rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr marker_pub;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SteerMarkerNode>());
    rclcpp::shutdown();
    return 0;
}
