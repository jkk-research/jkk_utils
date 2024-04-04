// Odoometrey from twist stamped message (/vehicle_status topic)
// publishes nav_msgs/Path 

#include <iostream>
#include <vector>
#include "rclcpp/rclcpp.hpp"
#include <geometry_msgs/msg/twist_stamped.hpp>

#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"
#include "tf2_ros/transform_broadcaster.h"

using namespace std::chrono_literals;
using std::placeholders::_1;

class Odom : public rclcpp::Node
{
public:
    Odom() : Node("odom_from_twiststamped")
    {
        this->declare_parameter<std::string>("status_topic", "lexus3/vehicle_status");
        this->declare_parameter<std::string>("odom_child_frame_id", "odom");
        this->declare_parameter<std::string>("map_frame_id", "map");
        this->declare_parameter<float>("wheelbase", wheelbase);
        this->get_parameter("status_topic", status_topic);
        this->get_parameter("wheelbase", wheelbase);
        this->get_parameter("odom_child_frame_id", odom_child_frame_id);
        this->get_parameter("map_frame_id", map_frame_id);
        tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        sub_status_ = this->create_subscription<geometry_msgs::msg::TwistStamped>(status_topic, 10, std::bind(&Odom::vehicleSteeringCallback, this, _1));
        timer_ = this->create_wall_timer(std::chrono::milliseconds(50), std::bind(&Odom::loop, this));
        RCLCPP_INFO_STREAM(this->get_logger(), "Node started: " << this->get_name() << " with status_topic: " << status_topic << " and wheelbase: " << wheelbase);
    }

private:
    // Callback for steering wheel and speed messages
    void vehicleSteeringCallback(const geometry_msgs::msg::TwistStamped &steer_msg)
    {
        vehicle_speed_mps = steer_msg.twist.linear.x;
        steering_angle = steer_msg.twist.angular.z;
        vehicleOdomCalc();
    }


    void vehicleOdomCalc()
    {
        if (!first_run)
        {
            dt = current_time - prev_time;
            //RCLCPP_INFO_STREAM(this->get_logger(), "dt: " << std::fixed << std::setprecision(3) << dt);
        }
        {
            // assumed 30 Hz
            dt = 0.033333;
        }
        if (first_run)
        {
            first_run = false;
        }
        odom_transform.header.stamp = this->get_clock()->now();
        odom_transform.header.frame_id = map_frame_id;
        odom_transform.child_frame_id = odom_child_frame_id;
        odom_transform.transform.translation.x += dt * vehicle_speed_mps * cos(theta);
        odom_transform.transform.translation.y += dt * vehicle_speed_mps * sin(theta);
        theta += dt * vehicle_speed_mps / wheelbase * tan(steering_angle);
        tf2::Quaternion theta_quat;
        theta_quat.setRPY(0.0, 0.0, theta);
        odom_transform.transform.rotation.w = theta_quat.getW();
        odom_transform.transform.rotation.x = theta_quat.getX();
        odom_transform.transform.rotation.y = theta_quat.getY();
        odom_transform.transform.rotation.z = theta_quat.getZ();
        tf_broadcaster_->sendTransform(odom_transform);
        prev_time = current_time;
    }

    void loop()
    {
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr sub_status_;
    std::string status_topic, odom_child_frame_id = "odom", map_frame_id = "map";
    double wheelbase = 2.789;
    double steering_angle, vehicle_speed_mps;
    long unsigned int path_size;
    bool steering_enabled;
    bool first_run = true, publish_steer_marker, publish_kmph;
    geometry_msgs::msg::TransformStamped odom_transform;
    std::string current_map = "empty";
    double theta = 0.0;
    double current_time, prev_time, dt;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Odom>());
    rclcpp::shutdown();
    return 0;
}
