#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from cofetch_msgs.msg import TaskInfo
from arm_control_node import ArmControlNode
from gripper_control_node import GripperControlNode
import time


class ManipulationExecutorNode(Node):
    def __init__(self):
        super().__init__('manipulation_executor_node')
        self.declare_parameter('approach_distance', 0.1)
        self.declare_parameter('retreat_distance', 0.15)
        self.declare_parameter('grasp_force', 5.0)
        self.declare_parameter('grasp_timeout', 10.0)

        self.approach_distance = self.get_parameter('approach_distance').value
        self.retreat_distance = self.get_parameter('retreat_distance').value
        self.grasp_force = self.get_parameter('grasp_force').value
        self.grasp_timeout = self.get_parameter('grasp_timeout').value

        self.arm_control = None
        self.gripper_control = None
        self.current_task = None

        self.task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/assigned',
            self.task_callback,
            10
        )

        self.get_logger().info('Manipulation Executor Node started')

    def task_callback(self, msg):
        if msg.task_type != 'pick_and_place':
            return

        self.current_task = msg
        self.execute_pick_and_place(msg)

    def execute_pick_and_place(self, task):
        try:
            self.get_logger().info(f'Executing pick and place for task {task.id}')

            self.arm_control.move_to_home()
            time.sleep(1.0)

            self.arm_control.move_to_pregrasp()
            time.sleep(1.0)

            self.gripper_control.open_gripper()
            time.sleep(0.5)

            self.arm_control.move_to_grasp()
            time.sleep(1.0)

            self.gripper_control.grasp(task.object_id)
            time.sleep(0.5)

            self.arm_control.move_to_retract()
            time.sleep(1.0)

            self.get_logger().info(f'Task {task.id} pick phase completed')

        except Exception as e:
            self.get_logger().error(f'Error executing task {task.id}: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = ManipulationExecutorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()