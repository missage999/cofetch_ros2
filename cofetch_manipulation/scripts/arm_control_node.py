#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from control_msgs.msg import JointControllerState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
import numpy as np


class ArmControlNode(Node):
    def __init__(self):
        super().__init__('arm_control_node')
        self.declare_parameter('max_velocity', 0.5)
        self.declare_parameter('max_acceleration', 1.0)
        self.declare_parameter('planning_timeout', 5.0)

        self.max_velocity = self.get_parameter('max_velocity').value
        self.max_acceleration = self.get_parameter('max_acceleration').value
        self.planning_timeout = self.get_parameter('planning_timeout').value

        self.joint_positions = [0.0, 0.0]
        self.target_joint_positions = [0.0, 0.0]

        self.joint_sub = self.create_subscription(
            JointControllerState,
            '/arm_joint_1_controller/state',
            self.joint_state_callback,
            10
        )

        self.arm_cmd_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        self.get_logger().info('Arm Control Node started')

    def joint_state_callback(self, msg):
        self.joint_positions[0] = msg.process_value

    def move_to_position(self, joint1_angle, joint2_angle):
        self.target_joint_positions = [joint1_angle, joint2_angle]

        trajectory = JointTrajectory()
        trajectory.joint_names = ['arm_joint_1', 'arm_joint_2']

        point = JointTrajectoryPoint()
        point.positions = self.target_joint_positions
        point.velocities = [0.0, 0.0]
        point.time_from_start.sec = 2

        trajectory.points.append(point)

        self.arm_cmd_pub.publish(trajectory)
        self.get_logger().info(f'Moving arm to position: [{joint1_angle:.2f}, {joint2_angle:.2f}]')

    def move_to_home(self):
        self.move_to_position(0.0, 0.0)

    def move_to_pregrasp(self):
        self.move_to_position(0.0, -0.5)

    def move_to_grasp(self):
        self.move_to_position(0.0, -1.0)

    def move_to_retract(self):
        self.move_to_position(-0.5, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = ArmControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()