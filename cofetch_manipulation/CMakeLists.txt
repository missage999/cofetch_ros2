cmake_minimum_required(VERSION 3.8)
project(cofetch_manipulation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(cofetch_msgs REQUIRED)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/arm_control_node.py scripts/gripper_control_node.py scripts/manipulation_executor_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()