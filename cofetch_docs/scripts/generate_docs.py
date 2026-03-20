#!/usr/bin/env python3

import os
import sys


def generate_api_docs(output_dir='/home/wangyu/ros2_ws/src/cofetch_ros2/docs/api'):
    print("Generating API documentation...")

    os.makedirs(output_dir, exist_ok=True)

    packages = [
        'cofetch_msgs',
        'cofetch_description',
        'cofetch_gazebo',
        'cofetch_config',
        'cofetch_deps',
        'cofetch_perception',
        'cofetch_exploration',
        'cofetch_scheduler',
        'cofetch_navigation',
        'cofetch_manipulation',
        'cofetch_bringup',
        'cofetch_ui',
        'cofetch_monitoring',
    ]

    for pkg in packages:
        pkg_dir = f'/home/wangyu/ros2_ws/src/cofetch_ros2/{pkg}'
        if os.path.exists(pkg_dir):
            print(f"  - {pkg}: OK")
        else:
            print(f"  - {pkg}: NOT FOUND")

    readme_content = """# Cofetch ROS2 API Documentation

This directory contains API documentation for the Cofetch project.

## Packages

"""

    for pkg in packages:
        readme_content += f"- [{pkg}](./{pkg}.md)\n"

    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.write(readme_content)

    print(f"\nAPI documentation generated in: {output_dir}")
    return True


def generate_install_docs():
    print("Generating installation documentation...")
    return True


def main():
    print("Cofetch Documentation Generator")
    print("=" * 40)

    success = generate_api_docs()

    if success:
        print("\nDocumentation generation completed!")
    else:
        print("\nDocumentation generation failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()