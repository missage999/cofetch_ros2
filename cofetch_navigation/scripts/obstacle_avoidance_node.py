#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Point, Pose, Twist
from nav_msgs.msg import Path
import numpy as np


class ObstacleAvoidanceNode(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_node')
        self.declare_parameter('safety_distance', 0.3)
        self.declare_parameter('detection_range', 1.0)
        self.declare_parameter('recovery_behavior', 'turn_in_place')

        self.safety_distance = self.get_parameter('safety_distance').value
        self.detection_range = self.get_parameter('detection_range').value
        self.recovery_behavior = self.get_parameter('recovery_behavior').value

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.cmd_vel_in_pub = self.create_subscription(
            Twist,
            '/cmd_vel_raw',
            self.cmd_vel_callback,
            10
        )

        self.cmd_vel_out_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.safe_path_pub = self.create_publisher(
            Point,
            '/navigation/safe_target',
            10
        )

        self.obstacle_detected = False

        self.get_logger().info('Obstacle Avoidance Node started')

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))

        min_range_in_front = np.min(ranges[(angles > -np.pi/4) & (angles < np.pi/4)])

        self.obstacle_detected = min_range_in_front < self.safety_distance

        if self.obstacle_detected:
            self.get_logger().warn(f'Obstacle detected at {min_range_in_front:.2f}m')

    def cmd_vel_callback(self, msg):
        if self.obstacle_detected:
            recovery_cmd = Twist()

            if self.recovery_behavior == 'turn_in_place':
                recovery_cmd.linear.x = 0.0
                recovery_cmd.angular.z = 0.5
            else:
                recovery_cmd.linear.x = 0.0
                recovery_cmd.angular.z = 0.3

            self.cmd_vel_out_pub.publish(recovery_cmd)
            self.get_logger().info('Executing obstacle avoidance recovery')
        else:
            self.cmd_vel_out_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()