#include "rclcpp/rclcpp.hpp"
#include "crio_msgs/msg/crio_message.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "builtin_interfaces/msg/time.hpp"

class CrioPublisher : public rclcpp::Node {
public:
    CrioPublisher() : Node("crio_publisher") {
        publisher_ = this->create_publisher<crio_msgs::msg::CrioMessage>("ctrl_cmd", 10);
        subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "cmd_vel", 10, std::bind(&CrioPublisher::twist_callback, this, std::placeholders::_1));
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100), std::bind(&CrioPublisher::publish_message, this));
    }

private:
    void twist_callback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        speed_ref_ = msg->linear.x;
        wheel_angle_ref_ = msg->angular.z;
    }

    void publish_message() {
        auto message = crio_msgs::msg::CrioMessage();
        message.timestamp = this->now();
        message.speed_ref = speed_ref_;
        message.wheel_angle_ref = wheel_angle_ref_;
        message.autonomous_system_ready = true;  // Example value
        message.autonomous_mode_operating = false;  // Example value
        publisher_->publish(message);
    }

    rclcpp::Publisher<crio_msgs::msg::CrioMessage>::SharedPtr publisher_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
    double speed_ref_ = 0.0;
    double wheel_angle_ref_ = 0.0;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CrioPublisher>());
    rclcpp::shutdown();
    return 0;
}