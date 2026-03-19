#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS_FILE="${SCRIPT_DIR}/../dependencies.yaml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Cofetch ROS2 Dependency Installer${NC}"
echo -e "${GREEN}========================================${NC}"

check_ros_distro() {
    if [ -z "$ROS_DISTRO" ]; then
        echo -e "${RED}Error: ROS_DISTRO is not set${NC}"
        echo "Please source your ROS2 setup file first:"
        echo "  source /opt/ros/jazzy/setup.bash"
        exit 1
    fi
    echo -e "${GREEN}ROS Distribution: $ROS_DISTRO${NC}"
}

check_ros_distro

install_apt_package() {
    local pkg=$1
    local desc=$2

    echo -e "${YELLOW}Installing: ${pkg}${NC}"
    echo "  ${desc}"

    if dpkg -l | grep -q "^ii  ${pkg} "; then
        echo -e "${GREEN}  Already installed${NC}"
        return 0
    fi

    sudo apt-get update -qq
    sudo apt-get install -y "${pkg}" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  Installed successfully${NC}"
        return 0
    else
        echo -e "${RED}  Failed to install${NC}"
        return 1
    fi
}

install_required_deps() {
    echo ""
    echo -e "${GREEN}[Required Dependencies]${NC}"
    echo "----------------------------------------"

    install_apt_package "python3-yaml" "PyYAML for Python"
    install_apt_package "python3-pip" "Python pip"

    echo ""
    echo -e "${GREEN}[Robot Packages]${NC}"
    echo "----------------------------------------"

    install_apt_package "ros-${ROS_DISTRO}-turtlebot4-description" "TurtleBot4 description"
    install_apt_package "ros-${ROS_DISTRO}-irobot-create-description" "iRobot Create3 description"
    install_apt_package "ros-${ROS_DISTRO}-turtlebot4-msgs" "TurtleBot4 messages"

    echo ""
    echo -e "${GREEN}[Gazebo Simulation]${NC}"
    echo "----------------------------------------"

    install_apt_package "ros-${ROS_DISTRO}-ros-gz-sim" "Gazebo Harmonic simulator"
    install_apt_package "ros-${ROS_DISTRO}-ros-gz-bridge" "ROS2 Gazebo bridge"
    install_apt_package "ros-${ROS_DISTRO}-ros-gz-image" "ROS2 Gazebo image bridge"
}

install_optional_deps() {
    echo ""
    echo -e "${YELLOW}[Optional Dependencies]${NC}"
    echo "----------------------------------------"
    echo "These are not required but provide additional functionality"
    echo ""

    local response
    read -p "Install optional dependencies? (y/n): " response

    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "Skipping optional dependencies"
        return 0
    fi

    install_apt_package "ros-${ROS_DISTRO}-navigation2" "Navigation2 stack"
    install_apt_package "ros-${ROS_DISTRO}-nav2-bringup" "Navigation2 bringup"
    install_apt_package "ros-${ROS_DISTRO}-image-pipeline" "Image processing pipeline"
    install_apt_package "ros-${ROS_DISTRO}-vision-opencv" "OpenCV vision packages"
}

verify_installation() {
    echo ""
    echo -e "${GREEN}[Verifying Installation]${NC}"
    echo "----------------------------------------"

    local missing=0

    check_package() {
        local pkg=$1
        if ! dpkg -l | grep -q "^ii  ${pkg} "; then
            echo -e "${RED}  Missing: ${pkg}${NC}"
            missing=$((missing + 1))
        else
            echo -e "${GREEN}  OK: ${pkg}${NC}"
        fi
    }

    check_package "ros-${ROS_DISTRO}-turtlebot4-description"
    check_package "ros-${ROS_DISTRO}-irobot-create-description"
    check_package "ros-${ROS_DISTRO}-ros-gz-sim"
    check_package "ros-${ROS_DISTRO}-ros-gz-bridge"

    if [ $missing -eq 0 ]; then
        echo ""
        echo -e "${GREEN}All required dependencies are installed!${NC}"
    else
        echo ""
        echo -e "${RED}${missing} packages are missing${NC}"
        return 1
    fi
}

main() {
    install_required_deps
    install_optional_deps
    verify_installation

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Build the workspace: colcon build"
    echo "  2. Source the workspace: source install/setup.bash"
    echo "  3. Launch the simulation: ros2 launch cofetch_gazebo gazebo.launch.py"
    echo ""
}

main "$@"