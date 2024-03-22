// publishes  /lexus3/vehicle_steering  and  /lexus3/vehicle_speed 

#include <iostream>
#include <vector>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include <pacmod3_msgs/msg/system_rpt_float.hpp>
#include <pacmod3_msgs/msg/vehicle_speed_rpt.hpp>

using namespace std::chrono_literals;
using std::placeholders::_1;

class TempNnPose : public rclcpp::Node
{
public:
    TempNnPose() : Node("temp_nn_pose_node")
    {
        sub_steer_ = this->create_subscription<pacmod3_msgs::msg::SystemRptFloat>("lexus3/pacmod/steering_rpt", 10, std::bind(&TempNnPose::vehicleSteeringCallback, this, _1));
        sub_speed_ = this->create_subscription<pacmod3_msgs::msg::VehicleSpeedRpt>("lexus3/pacmod/vehicle_speed_rpt", 10, std::bind(&TempNnPose::vehicleSpeedCallback, this, _1));
        pub_steer_ = this->create_publisher<std_msgs::msg::Float32>("lexus3/vehicle_steering", 10);
        pub_speed_ = this->create_publisher<std_msgs::msg::Float32>("lexus3/vehicle_speed", 10);
        RCLCPP_INFO_STREAM(this->get_logger(), "Node started: " << this->get_name());
    }

private:
    // Callback for steering wheel messages
    void vehicleSteeringCallback(const pacmod3_msgs::msg::SystemRptFloat &steer_msg)
    {
        steering_angle = steer_msg.output / 14.8;
        std_msgs::msg::Float32 steer_float_msg;
        steer_float_msg.data = steering_angle;
        pub_steer_->publish(steer_float_msg);
    }

    // Callback for vehicle speed messages
    void vehicleSpeedCallback(const pacmod3_msgs::msg::VehicleSpeedRpt &speed_msg)
    {
        vehicle_speed_mps = speed_msg.vehicle_speed;
        std_msgs::msg::Float32 speed_float_msg;
        speed_float_msg.data = vehicle_speed_mps;
        pub_speed_->publish(speed_float_msg);
    }

    rclcpp::Subscription<pacmod3_msgs::msg::SystemRptFloat>::SharedPtr sub_steer_;
    rclcpp::Subscription<pacmod3_msgs::msg::VehicleSpeedRpt>::SharedPtr sub_speed_;
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr pub_steer_;
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr pub_speed_;
    double steering_angle, vehicle_speed_mps;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TempNnPose>());
    rclcpp::shutdown();
    return 0;
}
