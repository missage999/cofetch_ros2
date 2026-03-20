#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import psutil
import time
import os


class PerformanceMonitorNode(Node):
    def __init__(self):
        super().__init__('performance_monitor_node')
        self.declare_parameter('monitoring_interval', 1.0)
        self.declare_parameter('enable_cpu', True)
        self.declare_parameter('enable_memory', True)

        self.monitoring_interval = self.get_parameter('monitoring_interval').value
        self.enable_cpu = self.get_parameter('enable_cpu').value
        self.enable_memory = self.get_parameter('enable_memory').value

        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()

        self.performance_pub = self.create_publisher(
            String,
            '/performance/metrics',
            10
        )

        self.timer = self.create_timer(self.monitoring_interval, self.publish_metrics)

        self.get_logger().info('Performance Monitor Node started')

    def publish_metrics(self):
        cpu_percent = self.process.cpu_percent(interval=0.1) if self.enable_cpu else 0.0
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024 if self.enable_memory else 0.0

        uptime = time.time() - self.start_time

        metrics = String()
        metrics.data = (
            f"timestamp: {time.time():.2f}, "
            f"cpu_percent: {cpu_percent:.2f}, "
            f"memory_mb: {memory_mb:.2f}, "
            f"uptime_s: {uptime:.2f}"
        )

        self.performance_pub.publish(metrics)
        self.get_logger().debug(f'Published metrics: {metrics.data}')


def main(args=None):
    rclpy.init(args=args)
    node = PerformanceMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()