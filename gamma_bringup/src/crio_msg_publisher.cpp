#include "rclcpp/rclcpp.hpp"
#include "crio_msgs/msg/crio_message.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "std_msgs/msg/bool.hpp"
#include "builtin_interfaces/msg/time.hpp"

class CrioPublisher : public rclcpp::Node {
public:
    CrioPublisher() : Node("crio_publisher") {
        publisher_ = this->create_publisher<crio_msgs::msg::CrioMessage>("ctrl_cmd", 10);
        subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "cmd_vel", 10, std::bind(&CrioPublisher::twist_callback, this, std::placeholders::_1));
        aut_dat_sub = this->create_subscription<std_msgs::msg::Bool>(
            "aut_dat", 10, std::bind(&CrioPublisher::autonomous_system_ready_callback, this, std::placeholders::_1)); 
        aut_sys_sub = this->create_subscription<std_msgs::msg::Bool>(
            "aut_sys", 10, std::bind(&CrioPublisher::autonomous_system_mode_callback, this, std::placeholders::_1));       
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100), std::bind(&CrioPublisher::publish_message, this));
    }

private:
    void twist_callback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        speed_ref_ = msg->linear.x;
        wheel_angle_ref_ = msg->angular.z;
    }
    void autonomous_system_ready_callback(const std_msgs::msg::Bool::SharedPtr msg) {
        aut_dat = msg->data;
    }

    void autonomous_system_mode_callback(const std_msgs::msg::Bool::SharedPtr msg) {
        aut_sys = msg->data;

    }        


    void publish_message() {
        auto message = crio_msgs::msg::CrioMessage();
        message.timestamp = this->now();
        message.speed_ref = speed_ref_;
        message.wheel_angle_ref = wheel_angle_ref_;
        message.autonomous_system_ready = aut_dat;  // Example value
        message.autonomous_mode_operating = aut_sys;  // Example value
        publisher_->publish(message);
    }

    rclcpp::Publisher<crio_msgs::msg::CrioMessage>::SharedPtr publisher_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr aut_dat_sub;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr aut_sys_sub;
    rclcpp::TimerBase::SharedPtr timer_;
    double speed_ref_ = 0.0;
    double wheel_angle_ref_ = 0.0;
    bool aut_dat, aut_sys;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CrioPublisher>());
    rclcpp::shutdown();
    return 0;
}