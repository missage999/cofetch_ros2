#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cofetch_msgs.msg import TaskInfo, TaskList
import time


class TaskExecutionMonitorNode(Node):
    def __init__(self):
        super().__init__('task_execution_monitor_node')
        self.declare_parameter('check_interval', 1.0)
        self.declare_parameter('failure_timeout', 60.0)
        self.declare_parameter('max_retries', 3)

        self.check_interval = self.get_parameter('check_interval').value
        self.failure_timeout = self.get_parameter('failure_timeout').value
        self.max_retries = self.get_parameter('max_retries').value

        self.tasks = {}
        self.task_start_times = {}
        self.task_retries = {}

        self.assigned_task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/assigned',
            self.assigned_task_callback,
            10
        )

        self.completed_task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/completed',
            self.completed_task_callback,
            10
        )

        self.failed_task_sub = self.create_subscription(
            TaskInfo,
            '/tasks/failed',
            self.failed_task_callback,
            10
        )

        self.task_status_pub = self.create_publisher(
            TaskInfo,
            '/tasks/status',
            10
        )

        self.task_list_pub = self.create_publisher(
            TaskList,
            '/tasks/all',
            10
        )

        self.timer = self.create_timer(self.check_interval, self.check_task_status)

        self.get_logger().info('Task Execution Monitor Node started')

    def assigned_task_callback(self, msg):
        self.tasks[msg.id] = msg
        self.task_start_times[msg.id] = time.time()
        self.task_retries[msg.id] = 0
        self.get_logger().info(f'Task {msg.id} started execution on robot {msg.assigned_robot}')

    def completed_task_callback(self, msg):
        if msg.id in self.tasks:
            msg.status = 'completed'
            self.tasks[msg.id] = msg
            self.publish_task_list()
            self.get_logger().info(f'Task {msg.id} completed successfully')

    def failed_task_callback(self, msg):
        if msg.id in self.tasks:
            self.task_retries[msg.id] = self.task_retries.get(msg.id, 0) + 1

            if self.task_retries[msg.id] < self.max_retries:
                msg.status = 'pending'
                msg.assigned_robot = ''
                self.tasks[msg.id] = msg
                self.get_logger().warn(f'Task {msg.id} failed, retry {self.task_retries[msg.id]}/{self.max_retries}')
            else:
                msg.status = 'failed'
                self.tasks[msg.id] = msg
                self.get_logger().error(f'Task {msg.id} failed permanently after {self.max_retries} retries')

            self.publish_task_list()

    def check_task_status(self):
        current_time = time.time()

        for task_id, start_time in self.task_start_times.items():
            if task_id not in self.tasks:
                continue

            task = self.tasks[task_id]

            if task.status == 'in_progress':
                elapsed = current_time - start_time
                if elapsed > self.failure_timeout:
                    self.get_logger().warn(f'Task {task_id} timed out after {elapsed:.1f}s')
                    task.status = 'failed'
                    self.tasks[task_id] = task

        self.publish_task_list()

    def publish_task_list(self):
        task_list = TaskList()
        task_list.tasks = list(self.tasks.values())
        self.task_list_pub.publish(task_list)

    def get_task_statistics(self):
        stats = {
            'total': len(self.tasks),
            'pending': 0,
            'assigned': 0,
            'in_progress': 0,
            'completed': 0,
            'failed': 0
        }

        for task in self.tasks.values():
            if task.status in stats:
                stats[task.status] += 1

        return stats


def main(args=None):
    rclpy.init(args=args)
    node = TaskExecutionMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()