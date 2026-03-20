#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class TopicBandwidthAnalyzer(Node):
    def __init__(self):
        super().__init__('topic_bandwidth_analyzer')
        self.declare_parameter('analyze_interval', 5.0)
        self.declare_parameter('monitored_topics', '["/scan", "/odom", "/cmd_vel"]')

        self.analyze_interval = self.get_parameter('analyze_interval').value

        self.topic_stats = {}
        self.topic_last_count = {}
        self.topic_last_time = {}

        self.timer = self.create_timer(self.analyze_interval, self.analyze_bandwidth)

        self.bandwidth_pub = self.create_publisher(
            String,
            '/performance/bandwidth',
            10
        )

        self.get_logger().info('Topic Bandwidth Analyzer started')

    def analyze_bandwidth(self):
        try:
            topic_names_and_types = self.get_topic_names_and_types()

            bandwidth_info = []
            current_time = time.time()

            for topic_name, topic_types in topic_names_and_types:
                if not topic_name.startswith('/'):
                    continue

                try:
                    count = self.get_subscription_count(topic_name)
                except:
                    count = 0

                if topic_name in self.topic_last_count:
                    msg_count = count - self.topic_last_count[topic_name]
                    time_diff = current_time - self.topic_last_time[topic_name]
                    bandwidth = (msg_count / time_diff) if time_diff > 0 else 0.0

                    bandwidth_info.append(f"{topic_name}: {bandwidth:.2f} Hz")

                self.topic_last_count[topic_name] = count
                self.topic_last_time[topic_name] = current_time

            if bandwidth_info:
                msg = String()
                msg.data = "\n".join(bandwidth_info)
                self.bandwidth_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f'Bandwidth analysis error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = TopicBandwidthAnalyzer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()