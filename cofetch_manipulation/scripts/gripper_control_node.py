#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import numpy as np


class GripperControlNode(Node):
    def __init__(self):
        super().__init__('gripper_control_node')
        self.declare_parameter('max_opening', 0.03)
        self.declare_parameter('max_force', 10.0)

        self.max_opening = self.get_parameter('max_opening').value
        self.max_force = self.get_parameter('max_force').value

        self.current_opening = 0.0
        self.target_opening = 0.0
        self.is_grasping = False
        self.grasped_object = None

        self.gripper_left_pub = self.create_publisher(
            Float64,
            '/gripper_left_controller/command',
            10
        )

        self.gripper_right_pub = self.create_publisher(
            Float64,
            '/gripper_right_controller/command',
            10
        )

        self.get_logger().info('Gripper Control Node started')

    def set_opening(self, opening):
        opening = np.clip(opening, 0.0, self.max_opening)
        self.target_opening = opening

        left_cmd = Float64()
        left_cmd.data = opening

        right_cmd = Float64()
        right_cmd.data = opening

        self.gripper_left_pub.publish(left_cmd)
        self.gripper_right_pub.publish(right_cmd)

        self.get_logger().info(f'Gripper opening set to {opening:.4f}m')

    def open_gripper(self):
        self.set_opening(self.max_opening)
        self.is_grasping = False
        self.grasped_object = None
        self.get_logger().info('Gripper opened')

    def close_gripper(self):
        self.set_opening(0.0)
        self.get_logger().info('Gripper closed')

    def grasp(self, object_id=None):
        self.set_opening(0.0)
        self.is_grasping = True
        self.grasped_object = object_id
        self.get_logger().info(f'Grasping object: {object_id if object_id else "unknown"}')

    def release(self):
        self.open_gripper()
        self.get_logger().info('Gripper released')

    def get_grasped_object(self):
        return self.grasped_object if self.is_grasping else None


def main(args=None):
    rclpy.init(args=args)
    node = GripperControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()