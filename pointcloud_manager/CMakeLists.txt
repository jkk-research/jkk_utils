cmake_minimum_required(VERSION 3.8)
project(pointcloud_manager)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


# find dependencies
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(geometry_msgs)
find_package(pcl_ros)
find_package(sensor_msgs)
find_package(std_msgs)
find_package(visualization_msgs)
find_package(ros2launch)
find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED NO_MODULE)
find_package(Boost REQUIRED)
find_package(PCL REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

set(dependencies 
  rclcpp
  rclcpp_lifecycle
  rclcpp_components
  geometry_msgs
  pcl_ros
  sensor_msgs
  std_msgs
  visualization_msgs
)

include_directories(
  include/pointcloud_manager
  ${Boost_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIR}
)

file(GLOB_RECURSE SOURCE_FILES
    ${CMAKE_SOURCE_DIR}/src/*.cpp)

file(GLOB_RECURSE HEADER_FILES
    ${CMAKE_SOURCE_DIR}/include/pointcloud_manager/*.h
    ${CMAKE_SOURCE_DIR}/include/pointcloud_manager/*.hpp)

add_executable(pointcloud_manager ${HEADER_FILES} ${SOURCE_FILES})
ament_target_dependencies(pointcloud_manager rclcpp rclcpp_components geometry_msgs std_msgs sensor_msgs pcl_ros visualization_msgs)
target_link_libraries(pointcloud_manager ${catkin_LIBRARIES} ${Eigen_LIBRARIES})


add_library(pcl_component SHARED
            src/pclmerger.cpp)

ament_target_dependencies(pcl_component
            ${dependencies})

target_link_libraries(pcl_component
  ${PCL_LIBRARIES}
  ${catkin_LIBRARIES} ${Eigen_LIBRARIES}
)

rclcpp_components_register_nodes(pcl_component
                                 PLUGIN "pointcloud_merger::PCLMerger"
                                 EXECUTABLE "pointcloud_merger")

ament_export_targets(pcl_component)
install(TARGETS pcl_component
        EXPORT pcl_component
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
)

target_include_directories(pointcloud_manager PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(pointcloud_manager PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17

install(TARGETS pointcloud_manager
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

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

  install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME})

ament_package()
