#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <math.h>

#include "rclcpp/rclcpp.hpp"

#include "geometry_msgs/msg/pose_stamped.hpp"
#include "novatel_oem7_msgs/msg/bestutm.hpp"

#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"


using namespace std::chrono_literals;
using std::placeholders::_1;

class PubLexus : public rclcpp::Node
{
  rcl_interfaces::msg::SetParametersResult parametersCallback(const std::vector<rclcpp::Parameter> &parameters)
  {
    rcl_interfaces::msg::SetParametersResult result;
    result.successful = true;
    result.reason = "success";
    for (const auto &param : parameters)
    {
      RCLCPP_INFO_STREAM(this->get_logger(), "Param update: " << param.get_name().c_str() << ": " << param.value_to_string().c_str());
      if (param.get_name() == "bestutm_topic")
      {
        bestutm_topic = param.as_string();
        sub_w_ = this->create_subscription<novatel_oem7_msgs::msg::BESTUTM>(bestutm_topic, 10, std::bind(&PubLexus::utmCallback, this, _1));
      }
      if (param.get_name() == "wheelbase")
      {
        wheelbase = param.as_double();
      }
    }
    return result;
  }

public:
  PubLexus() : Node("pub_lexus_node")
  {
    RCLCPP_INFO_STREAM(this->get_logger(), "pub_lexus_node started: ");
    this->declare_parameter<std::string>("bestutm_topic", "/lexus3/gps/nova/bestutm");
    this->declare_parameter<float>("wheelbase", wheelbase);
    this->get_parameter("bestutm_topic", bestutm_topic);
    this->get_parameter("wheelbase", wheelbase);

    goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("current_pose", 10);
    sub_w_ = this->create_subscription<novatel_oem7_msgs::msg::BESTUTM>(bestutm_topic, 10, std::bind(&PubLexus::utmCallback, this, _1));
    timer_ = this->create_wall_timer(50ms, std::bind(&PubLexus::timerLoop, this));
    callback_handle_ = this->add_on_set_parameters_callback(std::bind(&PubLexus::parametersCallback, this, std::placeholders::_1));
  }

private:

  void utmCallback(const novatel_oem7_msgs::msg::BESTUTM &msg) const
  {
    RCLCPP_INFO_STREAM(this->get_logger(), "utmCallback " << msg.easting << " " << msg.northing);
    geometry_msgs::msg::PoseStamped pose;
    pose.header.stamp = this->now();
    pose.header.frame_id = "map";
    pose.pose.position.x = msg.easting;
    pose.pose.position.y = msg.northing;
    pose.pose.position.z = 0.0;
    tf2::Quaternion q;
    q.setRPY(0, 0, 0);
    pose.pose.orientation.x = q.x();
    pose.pose.orientation.y = q.y();
    pose.pose.orientation.z = q.z();
    pose.pose.orientation.w = q.w();
    goal_pub_->publish(pose);
  }
  void timerLoop()
  {
    // RCLCPP_INFO_STREAM(this->get_logger(), "timer");
  }

  rclcpp::Subscription<novatel_oem7_msgs::msg::BESTUTM>::SharedPtr sub_w_;
  std::string bestutm_topic;
  // parameters
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  float wheelbase = 2.789;
  OnSetParametersCallbackHandle::SharedPtr callback_handle_;
};

int main(int argc, char **argv)
{

  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PubLexus>());
  rclcpp::shutdown();
  return 0;
}