cmake_minimum_required(VERSION 3.8)
project(cofetch_perception)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

find_package(cv_bridge REQUIRED)
find_package(vision_msgs REQUIRED)
find_package(cofetch_msgs REQUIRED)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/object_detection_node.py scripts/object_tracking_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()