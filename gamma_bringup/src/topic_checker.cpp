#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_msgs/msg/bool.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include <chrono>
#include <unordered_map>
#include <unordered_set>
#include <variant>

using namespace std::chrono_literals;

class TopicChecker : public rclcpp::Node {
public:
    TopicChecker() : Node("topic_checker"), all_received_(true) {
        // Define topics and their types
        topics_ = {
            {"topic_name1", "std_msgs/msg/String"},
            {"topic_name2", "std_msgs/msg/Bool"},
            {"topic_name3", "sensor_msgs/msg/PointCloud2"},
            {"lexus3/os_left/points", "sensor_msgs/msg/PointCloud2"}
        };

        for (const auto &topic : topics_) {
            message_received_[topic.first] = false;
            if (topic.second == "std_msgs/msg/String") {
                subscriptions_.push_back(this->create_subscription<std_msgs::msg::String>(
                    topic.first, 10, [this, topic](const std_msgs::msg::String::SharedPtr msg) {
                        //RCLCPP_INFO(this->get_logger(), "Received message on %s: '%s'", topic.first.c_str(), msg->data.c_str());
                        message_received_[topic.first] = true;
                    }));
            } else if (topic.second == "std_msgs/msg/Bool") {
                subscriptions_.push_back(this->create_subscription<std_msgs::msg::Bool>(
                    topic.first, 10, [this, topic](const std_msgs::msg::Bool::SharedPtr msg) {
                        //RCLCPP_INFO(this->get_logger(), "Received message on %s: '%s'", topic.first.c_str(), msg->data ? "true" : "false");
                        message_received_[topic.first] = true;
                    }));
            } else if (topic.second == "sensor_msgs/msg/PointCloud2") {
                subscriptions_.push_back(this->create_subscription<sensor_msgs::msg::PointCloud2>(
                    topic.first, 10, [this, topic](const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
                        if (msg->data.empty()) {
                            //RCLCPP_WARN(this->get_logger(), "Received empty PointCloud2 message on %s", topic.first.c_str());
                            message_received_[topic.first] = false;
                        } else {
                            //RCLCPP_INFO(this->get_logger(), "Received non-empty PointCloud2 message on %s", topic.first.c_str());
                            message_received_[topic.first] = true;
                        }
                    }));
            }
        }

        publisher_ = this->create_publisher<std_msgs::msg::Bool>("aut_dat", 10);
        timer_ = this->create_wall_timer(
            1s, std::bind(&TopicChecker::check_message_status, this));
        warning_timer_ = this->create_wall_timer(
            2s, std::bind(&TopicChecker::send_warnings, this));
        RCLCPP_INFO(this->get_logger(), "Node has been started.");
    }

private:
    void check_message_status() {
        all_received_ = true;
        missing_topics_.clear();
        for (const auto &topic : topics_) {
            if (!message_received_[topic.first]) {
                all_received_ = false;
                missing_topics_.insert(topic.first);
            }
            message_received_[topic.first] = false; // Reset the flag for the next check
        }

        auto message = std_msgs::msg::Bool();
        message.data = all_received_;
        publisher_->publish(message);
    }

    void send_warnings() {
        if (all_received_) {
            RCLCPP_INFO(this->get_logger(), "All topics received.");
        } else {
            for (const auto &topic : missing_topics_) {
                RCLCPP_WARN(this->get_logger(), "%s", topic.c_str());
            }
        }
    }

    std::vector<std::pair<std::string, std::string>> topics_;
    std::unordered_map<std::string, bool> message_received_;
    std::unordered_set<std::string> missing_topics_;
    std::vector<rclcpp::SubscriptionBase::SharedPtr> subscriptions_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr warning_timer_;
    bool all_received_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TopicChecker>());
    rclcpp::shutdown();
    return 0;
}
