cmake_minimum_required(VERSION 3.8)
project(autoware_speed_relay)

# Default to C++17
set(CMAKE_CXX_STANDARD 17)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(pacmod3_msgs REQUIRED)
find_package(autoware_control_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(rclcpp_components REQUIRED)  # os_pcl_merger_component 
find_package(pcl_ros REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

set(ament_dependencies
  rclcpp
  std_msgs
  pacmod3_msgs
  autoware_control_msgs
  geometry_msgs
  nav_msgs
  visualization_msgs
  tf2
  tf2_msgs
  tf2_ros
  tf2_geometry_msgs
  rclcpp_components
  pcl_ros
)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_executable(speed_relay src/speed_relay.cpp)
ament_target_dependencies(speed_relay ${ament_dependencies}) 
target_compile_features(speed_relay PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17

install(TARGETS speed_relay
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
