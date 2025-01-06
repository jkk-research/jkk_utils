#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_msgs/msg/bool.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "visualization_msgs/msg/marker_array.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "geometry_msgs/msg/pose_array.hpp"
#include "std_msgs/msg/float32.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "crio_msgs/msg/crio_message.hpp"
#include <chrono>
#include <unordered_map>
#include <unordered_set>
#include <variant>

using namespace std::chrono_literals;

class TopicChecker : public rclcpp::Node {
public:
    TopicChecker() : Node("topic_checker"), all_received_(true), check_sensors_(true) {
        this->declare_parameter<std::vector<std::string>>("topics_and_types", {});
        this->declare_parameter<std::vector<std::string>>("sensor_topics", {});
        this->declare_parameter<bool>("check_sensors", true);

        std::vector<std::string> topics_and_types;
        this->get_parameter("topics_and_types", topics_and_types);
        this->get_parameter("check_sensors", check_sensors_);

        if (topics_and_types.size() % 2 != 0) {
            RCLCPP_ERROR(this->get_logger(), "The topics_and_types parameter must contain an even number of elements.");
            return;
        }

        for (size_t i = 0; i < topics_and_types.size(); i += 2) {
            topics_.emplace_back(topics_and_types[i], topics_and_types[i + 1]);
        }

        for (const auto &topic : topics_) {
            message_received_[topic.first] = false;
            if (topic.second == "std_msgs/msg/String") {
                subscriptions_.push_back(this->create_subscription<std_msgs::msg::String>(
                    topic.first, 10, [this, topic](const std_msgs::msg::String::SharedPtr msg) {
                        if (topic.first == "gamma1/gps/duro/hea/status_string" ) {
                            if (msg->data == "Fixed RTK" || msg->data == "Float RTK") {
                                message_received_[topic.first] = true;
                            } else {
                                message_received_[topic.first] = false;
                            }
                        } else {
                            message_received_[topic.first] = true;
                        }
                    }));

            } else if (topic.second == "std_msgs/msg/Bool") {
                subscriptions_.push_back(this->create_subscription<std_msgs::msg::Bool>(
                    topic.first, 10, [this, topic](const std_msgs::msg::Bool::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));

            } else if (topic.second == "sensor_msgs/msg/PointCloud2") {
                subscriptions_.push_back(this->create_subscription<sensor_msgs::msg::PointCloud2>(
                    topic.first, 10, [this, topic](const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
                        if (msg->data.empty()) {
                            message_received_[topic.first] = false;
                        } else {
                            message_received_[topic.first] = true;
                        }
                    }));

            } else if (topic.second == "visualization_msgs/msg/MarkerArray") {
                subscriptions_.push_back(this->create_subscription<visualization_msgs::msg::MarkerArray>(
                    topic.first, 10, [this, topic](const visualization_msgs::msg::MarkerArray::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));

            } else if (topic.second == "geometry_msgs/msg/PoseStamped") {
                subscriptions_.push_back(this->create_subscription<geometry_msgs::msg::PoseStamped>(
                    topic.first, 10, [this, topic](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));
                    
            } else if (topic.second == "geometry_msgs/msg/PoseArray") {
                subscriptions_.push_back(this->create_subscription<geometry_msgs::msg::PoseArray>(
                    topic.first, 10, [this, topic](const geometry_msgs::msg::PoseArray::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));

            } else if (topic.second == "std_msgs/msg/Float32") {
                subscriptions_.push_back(this->create_subscription<std_msgs::msg::Float32>(
                    topic.first, 10, [this, topic](const std_msgs::msg::Float32::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));

            } else if (topic.second == "geometry_msgs/msg/Twist") {
                subscriptions_.push_back(this->create_subscription<geometry_msgs::msg::Twist>(
                    topic.first, 10, [this, topic](const geometry_msgs::msg::Twist::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));

            } else if (topic.second == "crio_msgs/msg/CrioMessage") {
                subscriptions_.push_back(this->create_subscription<crio_msgs::msg::CrioMessage>(
                    topic.first, 10, [this, topic](const crio_msgs::msg::CrioMessage::SharedPtr msg) {
                        message_received_[topic.first] = true;
                    }));
            } else {
                RCLCPP_ERROR(this->get_logger(), "Unsupported message type: %s", topic.second.c_str());
            }
        }

        if (check_sensors_) {
            std::vector<std::string> sensor_topics;
            this->get_parameter("sensor_topics", sensor_topics);

            if (sensor_topics.size() % 2 != 0) {
                RCLCPP_ERROR(this->get_logger(), "The sensor_topics parameter must contain an even number of elements.");
                return;
            }
            for (size_t i = 0; i < sensor_topics.size(); i += 2) {
                sensor_topics_.emplace_back(sensor_topics[i], sensor_topics[i + 1]);
            }

            for (const auto &sensor_topic :  sensor_topics_) {
                sensor_message_received_[sensor_topic.first] = false;

                if (sensor_topic.second == "sensor_msgs/msg/PointCloud2") {
                    subscriptions_.push_back(this->create_subscription<sensor_msgs::msg::PointCloud2>(
                        sensor_topic.first, 10, [this, sensor_topic](const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
                            if (msg->data.empty()) {
                                sensor_message_received_[sensor_topic.first] = false;
                            } else {
                                sensor_message_received_[sensor_topic.first] = true;
                            }
                        }));
                } else {
                    RCLCPP_ERROR(this->get_logger(), "Unsupported sensor message type: %s", sensor_topic.second.c_str());
                }
            }
        }

        publisher_ = this->create_publisher<std_msgs::msg::Bool>("aut_dat", 10);
        timer_ = this->create_wall_timer(
            1s, std::bind(&TopicChecker::check_message_status, this));
        warning_timer_ = this->create_wall_timer(
            2s, std::bind(&TopicChecker::send_warnings, this));
        if (check_sensors_) {
            sensor_warning_timer_ = this->create_wall_timer(
                2s, std::bind(&TopicChecker::send_sensor_warnings, this));
        }
        RCLCPP_INFO(this->get_logger(), "Node has been started.");
    }

private:
    void check_message_status() {
        all_received_ = true;
        sensor_all_received_ = true;
        missing_topics_.clear();
        sensor_missing_topics_.clear();

        for (const auto &topic : topics_) {
            if (!message_received_[topic.first]) {
                all_received_ = false;
                missing_topics_.insert(topic.first);
            }
            message_received_[topic.first] = false; // Reset the flag for the next check
        }

        if (check_sensors_) {
            for (const auto &sensor_topic :  sensor_topics_) {
                if (!sensor_message_received_[sensor_topic.first]) {
                    sensor_all_received_ = false;
                    sensor_missing_topics_.insert(sensor_topic.first);
                }
                sensor_message_received_[sensor_topic.first] = false; // Reset the flag for the next check
            }
        }

        auto message = std_msgs::msg::Bool();
        message.data = all_received_ && (!check_sensors_ || sensor_missing_topics_.size() <= 1);
        publisher_->publish(message);
    }

    void send_warnings() {
        if (all_received_) {
            RCLCPP_INFO(this->get_logger(), "All necessary topics received.");
        } else {
            for (const auto &topic : missing_topics_) {
                RCLCPP_WARN(this->get_logger(), "Missing topic: %s", topic.c_str());
            }
            RCLCPP_WARN(this->get_logger(), "--------");
        }
    }

    void send_sensor_warnings() {
        if (!sensor_all_received_) {
            for (const auto &sensor_topic : sensor_missing_topics_) {
                RCLCPP_WARN(this->get_logger(), "Missing sensor topic: %s", sensor_topic.c_str());
            }
            RCLCPP_WARN(this->get_logger(), "--------");
        }
    }

    std::vector<std::pair<std::string, std::string>> topics_;
    std::vector<std::pair<std::string, std::string>> sensor_topics_;
    std::unordered_map<std::string, bool> message_received_;
    std::unordered_map<std::string, bool> sensor_message_received_;
    std::unordered_set<std::string> missing_topics_;
    std::unordered_set<std::string> sensor_missing_topics_;
    std::vector<rclcpp::SubscriptionBase::SharedPtr> subscriptions_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr warning_timer_;
    rclcpp::TimerBase::SharedPtr sensor_warning_timer_;
    bool all_received_;
    bool sensor_all_received_;
    bool check_sensors_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TopicChecker>());
    rclcpp::shutdown();
    return 0;
}
