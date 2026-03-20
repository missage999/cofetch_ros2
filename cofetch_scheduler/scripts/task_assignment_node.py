#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from cofetch_msgs.msg import TaskInfo, RobotStatus
import numpy as np


class TaskAssignmentNode(Node):
    def __init__(self):
        super().__init__('task_assignment_node')
        self.declare_parameter('assignment_strategy', 'nearest')
        self.declare_parameter('load_balancing', True)
        self.declare_parameter('max_tasks_per_robot', 5)

        self.assignment_strategy = self.get_parameter('assignment_strategy').value
        self.load_balancing = self.get_parameter('load_balancing').value
        self.max_tasks_per_robot = self.get_parameter('max_tasks_per_robot').value

        self.tasks = {}
        self.robots = {}
        self.robot_task_counts = {}

        self.task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/new',
            self.task_callback,
            10
        )

        self.robot_status_sub = self.create_subscription(
            RobotStatus,
            '/robot_status',
            self.robot_status_callback,
            10
        )

        self.assigned_task_pub = self.create_publisher(
            TaskInfo,
            '/tasks/assigned',
            10
        )

        self.get_logger().info('Task Assignment Node started')

    def task_callback(self, msg):
        if msg.status != 'pending':
            return

        self.tasks[msg.id] = msg
        assigned_robot = self.assign_task(msg)

        if assigned_robot:
            msg.assigned_robot = assigned_robot
            msg.status = 'assigned'
            self.assigned_task_pub.publish(msg)

            if assigned_robot not in self.robot_task_counts:
                self.robot_task_counts[assigned_robot] = 0
            self.robot_task_counts[assigned_robot] += 1

            self.get_logger().info(f'Task {msg.id} assigned to {assigned_robot}')
        else:
            self.get_logger().warn(f'No available robot for task {msg.id}')

    def robot_status_callback(self, msg):
        self.robots[msg.id] = msg

    def assign_task(self, task):
        available_robots = [
            robot_id for robot_id, status in self.robots.items()
            if status.status == 'idle'
        ]

        if not available_robots:
            return None

        if self.load_balancing:
            available_robots = [
                r for r in available_robots
                if self.robot_task_counts.get(r, 0) < self.max_tasks_per_robot
            ]

        if not available_robots:
            return None

        if self.assignment_strategy == 'nearest':
            return self.assign_nearest(task, available_robots)
        else:
            return available_robots[0]

    def assign_nearest(self, task, available_robots):
        task_pos = np.array([task.target_position.x, task.target_position.y])

        min_distance = float('inf')
        nearest_robot = None

        for robot_id in available_robots:
            robot_pos = np.array([
                self.robots[robot_id].position.x,
                self.robots[robot_id].position.y
            ])

            distance = np.linalg.norm(task_pos - robot_pos)

            if distance < min_distance:
                min_distance = distance
                nearest_robot = robot_id

        return nearest_robot


def main(args=None):
    rclpy.init(args=args)
    node = TaskAssignmentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()