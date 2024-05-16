#include "pclmerger.hpp"

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_components/register_node_macro.hpp>

namespace pointcloud_merger{
  PCLMerger::PCLMerger(string& node_name) : 
  Node(node_name, rclcpp::NodeOptions().use_intra_process_comms(true))
  {
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

    initData();

    for(unsigned int i=0; i<vector_of_topic_names.size(); i++){
      pcl::PointCloud<pcl::PointXYZI>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZI>());
      vector_of_clouds.push_back(cloud);
    }

    rmw_qos_profile_t qos_profile = rmw_qos_profile_sensor_data;
    auto qos = rclcpp::QoS(rclcpp::QoSInitialization(qos_profile.history, 1), qos_profile);

    auto bound_callback_func = std::bind(&PCLMerger::callbackCommon, this, std::placeholders::_1);
    
    for(unsigned int i=0; i<vector_of_clouds.size(); i++){
      vector_of_subscriptions.push_back(this->create_subscription<sensor_msgs::msg::PointCloud2>(vector_of_topic_names[i], qos, bound_callback_func));
    }

    timer_for_publishing_ = this->create_wall_timer(50ms, std::bind(&PCLMerger::publish_pcl_callback, this));

    this->concatenated_cloud_pub = this->create_publisher<sensor_msgs::msg::PointCloud2>("concatenated_points", 1);
  }

  PCLMerger::PCLMerger(const rclcpp::NodeOptions & options) : 
  Node("pointcloud_merger", options)
  {
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

    initData();

    for(unsigned int i=0; i<vector_of_topic_names.size(); i++){
      pcl::PointCloud<pcl::PointXYZI>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZI>());
      vector_of_clouds.push_back(cloud);
    }

    rmw_qos_profile_t qos_profile = rmw_qos_profile_sensor_data;
    auto qos = rclcpp::QoS(rclcpp::QoSInitialization(qos_profile.history, 1), qos_profile);

    auto bound_callback_func = std::bind(&PCLMerger::callbackCommon, this, std::placeholders::_1);
    
    for(unsigned int i=0; i<vector_of_clouds.size(); i++){
      vector_of_subscriptions.push_back(this->create_subscription<sensor_msgs::msg::PointCloud2>(vector_of_topic_names[i], qos, bound_callback_func));
    }
    
    timer_for_publishing_ = this->create_wall_timer(50ms, std::bind(&PCLMerger::publish_pcl_callback, this));

    this->concatenated_cloud_pub = this->create_publisher<sensor_msgs::msg::PointCloud2>("concatenated_points", 1);
  }

  void PCLMerger::initData(){
    this->declare_parameter("topics", rclcpp::PARAMETER_STRING_ARRAY);
    this->declare_parameter("frames", rclcpp::PARAMETER_STRING_ARRAY);
    this->declare_parameter("child_frames", rclcpp::PARAMETER_STRING_ARRAY);

    rclcpp::Parameter topic_parameter = this->get_parameter("topics");
    rclcpp::Parameter frame_parameter = this->get_parameter("frames");
    rclcpp::Parameter child_frame_parameter = this->get_parameter("child_frames");

    this->vector_of_topic_names = topic_parameter.as_string_array();
    this->vector_of_frames = frame_parameter.as_string_array();
    this->vector_of_child_frames = child_frame_parameter.as_string_array();
  }

  void PCLMerger::callbackCommon(const sensor_msgs::msg::PointCloud2::ConstSharedPtr& msg){
    string target_frame = "world";
    geometry_msgs::msg::TransformStamped transform;
    for(unsigned int i=0; i<vector_of_clouds.size(); i++){
      if(msg->header.frame_id.c_str() == vector_of_frames[i]){
        pcl::fromROSMsg(*msg, *vector_of_clouds[i]);
        try {
          transform = tf_buffer_->lookupTransform(target_frame, msg->header.frame_id, tf2::TimePointZero);
          pcl_ros::transformPointCloud(*vector_of_clouds[i], *vector_of_clouds[i], transform);
          vector_of_clouds[i]->header.frame_id = target_frame;
          break;
        } catch (const tf2::TransformException & ex) {
          RCLCPP_INFO( this->get_logger(), "Could not transform %s to %s: %s", target_frame.c_str(), vector_of_clouds[i]->header.frame_id.c_str(), ex.what());
          return;
        }
      }
    }
  }

  void PCLMerger::publish_pcl_callback(){
    // Initialization of variables
    pcl::PointCloud<pcl::PointXYZI> result_cloud;
    sensor_msgs::msg::PointCloud2 result_message;

    int data = 0;
    for(unsigned int i=0; i<vector_of_clouds.size(); i++){
      result_cloud += *vector_of_clouds[i];
      if(!vector_of_clouds[i]->empty()){
        data++;
      }
    }
    
    result_cloud.header.frame_id = "world";
    pcl::toROSMsg(result_cloud, result_message);
    concatenated_cloud_pub->publish(result_message);
    if(data==vector_of_clouds.size()){
      for(unsigned int i=0; i<vector_of_clouds.size(); i++){
        vector_of_clouds[i]->clear();
      }
    }
  }
}

RCLCPP_COMPONENTS_REGISTER_NODE(pointcloud_merger::PCLMerger);