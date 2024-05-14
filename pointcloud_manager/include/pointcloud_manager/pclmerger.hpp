#ifndef PCLMERGER_HPP
#define PCLMERGER_HPP

#include <iostream>
#include <rclcpp/rclcpp.hpp>

#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>

#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_types.h>
#include <pcl/PCLPointCloud2.h>
#include <pcl/conversions.h>
#include <pcl/common/transforms.h>
#include <pcl_ros/transforms.hpp>

#include <message_filters/subscriber.h>
#include <message_filters/synchronizer.h>
#include <message_filters/sync_policies/approximate_time.h> 
#include <message_filters/message_event.h>

#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"

#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <Eigen/Core>

#include "tf2_ros/transform_broadcaster.h"

#include <chrono>
#include <functional>
#include <memory>
#include <vector>
#include <functional>
#include <map>

using std::cout;
using std::string;
using std::vector;
using namespace std::chrono_literals;

typedef message_filters::sync_policies::ApproximateTime<sensor_msgs::msg::PointCloud2, sensor_msgs::msg::PointCloud2> MySyncPolicy;

namespace pointcloud_merger{
    class PCLMerger : public rclcpp::Node{
    protected:
        rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr concatenated_cloud_pub;
        vector<string> vector_of_frames;
        vector<string> vector_of_topic_names;
        vector<string> vector_of_child_frames;
        vector<pcl::PointCloud<pcl::PointXYZI>::Ptr> vector_of_clouds;
        vector<rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr> vector_of_subscriptions;
        std::string topic_name_sub;
        std::shared_ptr<tf2_ros::TransformListener> tf_listener_{nullptr};
        std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::TimerBase::SharedPtr timer_for_publishing_;
        std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
    public:
        PCLMerger(string& node_name);
        PCLMerger(const rclcpp::NodeOptions & options);
        void initData();
        void callbackCommon(const sensor_msgs::msg::PointCloud2::ConstSharedPtr& msg);
        void publish_pcl_callback();
        void broadcast_timer_callback();
    };
}

#endif // PCLMERGER_HPP