#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from cofetch_msgs.msg import TaskInfo, TaskList, ObjectInfo
import uuid
import time


class TaskGenerationNode(Node):
    def __init__(self):
        super().__init__('task_generation_node')
        self.declare_parameter('auto_generation', True)
        self.declare_parameter('generation_interval', 2.0)

        self.auto_generation = self.get_parameter('auto_generation').value
        self.generation_interval = self.get_parameter('generation_interval').value

        self.tasks = []
        self.task_counter = 0

        self.object_sub = self.create_subscription(
            ObjectInfo,
            '/objects',
            self.object_callback,
            10
        )

        self.task_list_pub = self.create_publisher(
            TaskList,
            '/tasks',
            10
        )

        self.task_pub = self.create_publisher(
            TaskInfo,
            '/tasks/new',
            10
        )

        if self.auto_generation:
            self.timer = self.create_timer(self.generation_interval, self.generate_auto_tasks)

        self.get_logger().info('Task Generation Node started')

    def object_callback(self, msg):
        existing_task = None
        for task in self.tasks:
            if task.object_id == msg.id and task.status == 'pending':
                existing_task = task
                break

        if existing_task is None and not msg.is_grasped:
            self.create_pick_task(msg)

    def create_pick_task(self, obj):
        self.task_counter += 1
        task_id = f'task_{self.task_counter:04d}'

        priority = self.get_color_priority(obj.color)

        task = TaskInfo()
        task.id = task_id
        task.task_type = 'pick_and_place'
        task.object_id = obj.id
        task.object_color = obj.color
        task.target_position = obj.position
        task.priority = float(priority)
        task.status = 'pending'
        task.assigned_robot = ''

        self.tasks.append(task)
        self.publish_task(task)

        self.get_logger().info(f'Created task {task_id}: pick {obj.color} {obj.shape} at ({obj.position.x:.2f}, {obj.position.y:.2f})')

    def get_color_priority(self, color):
        priorities = {'red': 3, 'green': 2, 'blue': 1}
        return priorities.get(color, 0)

    def generate_auto_tasks(self):
        pass

    def publish_task(self, task):
        self.task_pub.publish(task)
        self.publish_task_list()

    def publish_task_list(self):
        task_list_msg = TaskList()
        task_list_msg.tasks = self.tasks
        self.task_list_pub.publish(task_list_msg)

    def get_pending_tasks(self):
        return [t for t in self.tasks if t.status == 'pending']

    def get_active_tasks(self):
        return [t for t in self.tasks if t.status == 'in_progress']


def main(args=None):
    rclpy.init(args=args)
    node = TaskGenerationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()