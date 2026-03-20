#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cofetch_msgs.msg import RobotStatus, TaskInfo, ObjectList, SystemStatus
from std_msgs.msg import String
import time


class StatusDisplayNode(Node):
    def __init__(self):
        super().__init__('status_display_node')
        self.declare_parameter('update_rate', 1.0)

        self.update_rate = self.get_parameter('update_rate').value

        self.robot_status = {}
        self.tasks = []
        self.objects = []
        self.system_status = None

        self.robot_status_sub = self.create_subscription(
            RobotStatus,
            '/robot_status',
            self.robot_status_callback,
            10
        )

        self.task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/all',
            self.task_callback,
            10
        )

        self.object_sub = self.create_subscription(
            ObjectList,
            '/objects',
            self.object_callback,
            10
        )

        self.system_status_sub = self.create_subscription(
            SystemStatus,
            '/system_status',
            self.system_status_callback,
            10
        )

        self.timer = self.create_timer(self.update_rate, self.display_status)

        self.get_logger().info('Status Display Node started')

    def robot_status_callback(self, msg):
        self.robot_status[msg.id] = msg

    def task_callback(self, msg):
        self.tasks = msg.tasks if hasattr(msg, 'tasks') else []

    def object_callback(self, msg):
        self.objects = msg.objects if hasattr(msg, 'objects') else []

    def system_status_callback(self, msg):
        self.system_status = msg

    def display_status(self):
        print('\033[2J\033[H')
        print('=' * 60)
        print('  Cofetch ROS2 System Status')
        print('=' * 60)

        print('\n[Robot Status]')
        if self.robot_status:
            for robot_id, status in self.robot_status.items():
                print(f'  {robot_id}: {status.status}, battery={status.battery_level:.1%}, task={status.current_task_id or "none"}')
        else:
            print('  No robots connected')

        print('\n[Task Status]')
        task_counts = {'pending': 0, 'assigned': 0, 'in_progress': 0, 'completed': 0, 'failed': 0}
        for task in self.tasks:
            if task.status in task_counts:
                task_counts[task.status] += 1
        print(f'  Pending: {task_counts["pending"]}, Assigned: {task_counts["assigned"]}, In Progress: {task_counts["in_progress"]}')
        print(f'  Completed: {task_counts["completed"]}, Failed: {task_counts["failed"]}')

        print('\n[Objects Detected]')
        color_counts = {'red': 0, 'green': 0, 'blue': 0}
        for obj in self.objects:
            if obj.color in color_counts:
                color_counts[obj.color] += 1
        print(f'  Red: {color_counts["red"]}, Green: {color_counts["green"]}, Blue: {color_counts["blue"]}')

        print('\n' + '=' * 60)
        print(f'  Updated: {time.strftime("%Y-%m-%d %H:%M:%S")}')
        print('=' * 60)


def main(args=None):
    rclpy.init(args=args)
    node = StatusDisplayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()