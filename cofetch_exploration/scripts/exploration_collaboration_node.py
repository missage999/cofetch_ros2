#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from cofetch_msgs.msg import FrontierInfo
import numpy as np


class CollaborationNode(Node):
    def __init__(self):
        super().__init__('exploration_collaboration_node')
        self.declare_parameter('min_robot_distance', 1.0)
        self.declare_parameter('shared_map_enabled', True)

        self.min_robot_distance = self.get_parameter('min_robot_distance').value
        self.shared_map_enabled = self.get_parameter('shared_map_enabled').value

        self.robot_positions = {}

        self.frontier_sub = self.create_subscription(
            FrontierInfo,
            '/frontiers',
            self.frontier_callback,
            10
        )

        self.coordinated_frontier_pub = self.create_publisher(
            FrontierInfo,
            '/coordinated_frontiers',
            10
        )

        self.get_logger().info('Exploration Collaboration Node started')

    def frontier_callback(self, msg):
        robot_name = msg.robot_name

        if robot_name not in self.robot_positions:
            self.robot_positions[robot_name] = msg.centroid

        self.robot_positions[robot_name] = msg.centroid

        if self.shared_map_enabled:
            coordinated_msg = self.assign_frontier_to_robot(msg)
            if coordinated_msg:
                self.coordinated_frontier_pub.publish(coordinated_msg)

    def assign_frontier_to_robot(self, frontier):
        assigned_robot = frontier.robot_name
        min_distance = float('inf')

        for robot_name, position in self.robot_positions.items():
            if robot_name == frontier.robot_name:
                continue

            distance = np.sqrt(
                (frontier.centroid.x - position.x)**2 +
                (frontier.centroid.y - position.y)**2
            )

            if distance < min_distance:
                min_distance = distance
                assigned_robot = robot_name

        if min_distance < self.min_robot_distance:
            self.get_logger().debug(
                f'Frontier conflict detected between robots at distance {min_distance:.2f}'
            )
            return None

        frontier.robot_name = assigned_robot
        return frontier

    def get_robot_positions(self):
        return self.robot_positions


def main(args=None):
    rclpy.init(args=args)
    node = CollaborationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()