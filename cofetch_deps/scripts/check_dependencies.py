#!/usr/bin/env python3

import subprocess
import sys
import yaml


def run_command(cmd, description):
    print(f"\n[CHECK] {description}")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"  Status: OK")
            return True, result.stdout
        else:
            print(f"  Status: FAILED")
            print(f"  Error: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"  Status: TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"  Status: ERROR - {e}")
        return False, str(e)


def check_ros_distro():
    ros_distro = subprocess.run(
        ['bash', '-c', 'echo $ROS_DISTRO'],
        capture_output=True,
        text=True
    ).stdout.strip()

    if not ros_distro:
        print("[ERROR] ROS_DISTRO is not set")
        print("  Please source your ROS2 setup file first:")
        print("    source /opt/ros/jazzy/setup.bash")
        return None

    print(f"[INFO] ROS Distribution: {ros_distro}")
    return ros_distro


def check_apt_package(package_name):
    result = subprocess.run(
        ['dpkg', '-l', package_name],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def check_ros_package(package_name):
    result = subprocess.run(
        ['ros2', 'pkg', 'list'],
        capture_output=True,
        text=True
    )
    return package_name in result.stdout


def main():
    print("=" * 50)
    print("  Cofetch ROS2 Dependency Checker")
    print("=" * 50)

    ros_distro = check_ros_distro()
    if not ros_distro:
        sys.exit(1)

    print("\n[CHECK] Required System Packages")
    print("-" * 40)
    system_packages = ['python3-yaml', 'python3-pip']
    for pkg in system_packages:
        status = check_apt_package(pkg)
        print(f"  {'OK' if status else 'MISSING'}: {pkg}")

    print("\n[CHECK] Required ROS Packages")
    print("-" * 40)
    ros_packages = [
        'turtlebot4_description',
        'irobot_create_description',
        'turtlebot4_msgs',
        'ros_gz_sim',
        'ros_gz_bridge',
        'ros_gz_image',
    ]

    missing = []
    for pkg in ros_packages:
        status = check_ros_package(pkg)
        print(f"  {'OK' if status else 'MISSING'}: {pkg}")
        if not status:
            missing.append(pkg)

    print("\n[CHECK] Gazebo")
    print("-" * 40)
    result, _ = run_command(['gz', 'sim', '--version'], "Gazebo version")
    if result:
        print(f"  Version: {_.strip()}")

    print("\n" + "=" * 50)
    if missing:
        print("RESULT: Some packages are missing")
        print("\nTo install missing packages, run:")
        print("  ./cofetch_deps/scripts/install_dependencies.sh")
        sys.exit(1)
    else:
        print("RESULT: All dependencies are installed!")
        sys.exit(0)


if __name__ == '__main__':
    main()