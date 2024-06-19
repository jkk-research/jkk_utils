#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <math.h>

#include "rclcpp/rclcpp.hpp"

#include "geometry_msgs/msg/pose_stamped.hpp"

#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"
#include "tf2_ros/transform_broadcaster.h"

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
        sub_w_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(bestutm_topic, 10, std::bind(&PubLexus::utmCallback, this, _1));
      }
      if (param.get_name() == "wheelbase")
      {
        wheelbase = param.as_double();
      }
    }
    return result;
  }

public:
  PubLexus() : Node("pub_gps_node")
  {
    RCLCPP_INFO_STREAM(this->get_logger(), "pub_gps_node started");
    this->declare_parameter<std::string>("bestutm_topic", "/lexus3/gps/nova/bestutm");
    this->declare_parameter<float>("wheelbase", wheelbase);
    this->declare_parameter<std::string>("pose_topic", "/current_pose");
    this->declare_parameter<std::string>("frame_id", "map");
    this->declare_parameter<std::string>("child_frame_id", "base_link");
    this->declare_parameter<float>("offset_x", 0.0);
    this->declare_parameter<float>("offset_y", 0.0);
    this->get_parameter("bestutm_topic", bestutm_topic);
    this->get_parameter("wheelbase", wheelbase);
    this->get_parameter("pose_topic", pose_topic);
    this->get_parameter("frame_id", frame_id);
    this->get_parameter("child_frame_id", child_frame_id);
    this->get_parameter("offset_x", offset_x);
    this->get_parameter("offset_y", offset_y);

    // goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("current_pose", 10);
    sub_w_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(pose_topic, 10, std::bind(&PubLexus::utmCallback, this, _1));
    timer_ = this->create_wall_timer(50ms, std::bind(&PubLexus::timerLoop, this));
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    callback_handle_ = this->add_on_set_parameters_callback(std::bind(&PubLexus::parametersCallback, this, std::placeholders::_1));
  }

private:

  void utmCallback(const geometry_msgs::msg::PoseStamped &msg)
  {
    RCLCPP_INFO_STREAM_ONCE(this->get_logger(), "Publlishing pose as tf " << pose_topic << " " << frame_id << " " << child_frame_id);
    geometry_msgs::msg::TransformStamped transform_to_send;
    // transform_to_send.header.stamp = this->get_clock()->now(); //msg.header.stamp;
    transform_to_send.header.stamp = msg.header.stamp;
    transform_to_send.header.frame_id = frame_id;
    transform_to_send.child_frame_id = child_frame_id;
    transform_to_send.transform.translation.x = msg.pose.position.x + offset_x;
    transform_to_send.transform.translation.y = msg.pose.position.y + offset_y;
    transform_to_send.transform.translation.z = 0.0;
    transform_to_send.transform.rotation = msg.pose.orientation;
    tf_broadcaster_->sendTransform(transform_to_send);

  }
  void timerLoop()
  {
    // RCLCPP_INFO_STREAM(this->get_logger(), "timer");
  }

  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_w_;
  std::string bestutm_topic;
  // parameters
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  std::string pose_topic, frame_id, child_frame_id;
  double offset_x, offset_y;
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