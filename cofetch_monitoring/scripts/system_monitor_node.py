#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cofetch_msgs.msg import RobotStatus, TaskInfo, SystemStatus, LogMsg
from std_msgs.msg import String
import time


class SystemMonitorNode(Node):
    def __init__(self):
        super().__init__('system_monitor_node')
        self.declare_parameter('log_level', 'info')
        self.declare_parameter('heartbeat_timeout', 5.0)

        self.log_level = self.get_parameter('log_level').value
        self.heartbeat_timeout = self.get_parameter('heartbeat_timeout').value

        self.last_robot_heartbeat = {}
        self.error_count = 0
        self.start_time = time.time()

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

        self.system_status_pub = self.create_publisher(
            SystemStatus,
            '/system_status',
            10
        )

        self.log_pub = self.create_publisher(
            LogMsg,
            '/system_log',
            10
        )

        self.timer = self.create_timer(1.0, self.monitor_loop)

        self.get_logger().info('System Monitor Node started')

    def robot_status_callback(self, msg):
        self.last_robot_heartbeat[msg.id] = time.time()

        if msg.status == 'error':
            self.error_count += 1
            self.publish_log('error', 'robot', f'Robot {msg.id} reported error status')

    def task_callback(self, msg):
        for task in msg.tasks:
            if task.status == 'failed':
                self.publish_log('warn', 'scheduler', f'Task {task.id} failed')

    def monitor_loop(self):
        current_time = time.time()

        for robot_id, last_heartbeat in list(self.last_robot_heartbeat.items()):
            if current_time - last_heartbeat > self.heartbeat_timeout:
                self.publish_log('error', 'monitor', f'Robot {robot_id} heartbeat timeout')
                del self.last_robot_heartbeat[robot_id]

        uptime = current_time - self.start_time

        system_status = SystemStatus()
        system_status.status = 'running' if self.error_count == 0 else 'error'
        system_status.cpu_usage = 0.0
        system_status.memory_usage = 0.0
        system_status.network_status = 1.0
        system_status.active_robots = len(self.last_robot_heartbeat)
        system_status.pending_tasks = 0
        system_status.error_message = '' if self.error_count == 0 else f'{self.error_count} errors detected'

        self.system_status_pub.publish(system_status)

    def publish_log(self, level, module, message):
        log_msg = LogMsg()
        log_msg.level = level
        log_msg.module = module
        log_msg.message = message
        log_msg.timestamp = str(time.time())
        self.log_pub.publish(log_msg)
        self.get_logger().info(f'[{level.upper()}] {module}: {message}')


def main(args=None):
    rclpy.init(args=args)
    node = SystemMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()