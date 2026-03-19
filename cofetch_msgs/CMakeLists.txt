cmake_minimum_required(VERSION 3.8)
project(cofetch_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObjectInfo.msg"
  "msg/ObjectList.msg"
  "msg/TaskInfo.msg"
  "msg/TaskList.msg"
  "msg/RobotStatus.msg"
  "msg/FrontierInfo.msg"
  "msg/PathInfo.msg"
  "msg/NavStatus.msg"
  "msg/SystemStatus.msg"
  "msg/LogMsg.msg"
  "srv/GetRobotStatus.srv"
  "srv/GetTaskStatus.srv"
  "srv/GetConfig.srv"
  "srv/SetConfig.srv"
  "srv/GetSystemStatus.srv"
  "action/Explore.action"
  "action/PickObject.action"
  "action/PlaceObject.action"
  "action/NavigateTo.action"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_generators)

ament_package()