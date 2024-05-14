#include "pclmerger.hpp"

int main(int argc, char ** argv)
{
  (void)argc;
  (void)argv;
  string node_name = "pointcloud_merger";
  
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<pointcloud_merger::PCLMerger>(node_name));
  rclcpp::shutdown();

  return 0;
}
