#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cofetch_msgs.msg import FrontierInfo, TaskInfo
from geometry_msgs.msg import Point
import numpy as np


class ExplorationCoordinatorNode(Node):
    def __init__(self):
        super().__init__('exploration_coordinator_node')
        self.declare_parameter('exploration_timeout', 600.0)
        self.declare_parameter('goal_tolerance', 0.5)

        self.exploration_timeout = self.get_parameter('exploration_timeout').value
        self.goal_tolerance = self.get_parameter('goal_tolerance').value

        self.frontiers = []
        self.current_target = None
        self.exploration_start_time = None
        self.exploration_complete = False

        self.frontier_sub = self.create_subscription(
            FrontierInfo,
            '/frontiers',
            self.frontier_callback,
            10
        )

        self.explore_action_server = None

        self.goal_pub = self.create_publisher(
            Point,
            '/exploration/target',
            10
        )

        self.status_pub = self.create_publisher(
            TaskInfo,
            '/exploration/status',
            10
        )

        self.timer = self.create_timer(1.0, self.check_exploration_progress)

        self.get_logger().info('Exploration Coordinator Node started')

    def frontier_callback(self, msg):
        existing_idx = None
        for i, f in enumerate(self.frontiers):
            if f.robot_name == msg.robot_name:
                existing_idx = i
                break

        if existing_idx is not None:
            self.frontiers[existing_idx] = msg
        else:
            self.frontiers.append(msg)

        if self.current_target is None and not self.exploration_complete:
            self.select_next_frontier()

    def select_next_frontier(self):
        if not self.frontiers:
            return

        unassigned = [f for f in self.frontiers if not f.is_assigned]
        if not unassigned:
            self.get_logger().info('All frontiers assigned, exploration may be complete')
            return

        best_frontier = min(unassigned, key=lambda f: f.value, reverse=True)

        self.current_target = best_frontier
        goal_msg = Point()
        goal_msg.x = best_frontier.centroid.x
        goal_msg.y = best_frontier.centroid.y
        goal_msg.z = 0.0
        self.goal_pub.publish(goal_msg)

        self.get_logger().info(f'Selected frontier at ({goal_msg.x:.2f}, {goal_msg.y:.2f})')

    def check_exploration_progress(self):
        if self.exploration_complete:
            return

        if self.current_target is not None:
            distance_to_goal = np.sqrt(
                self.current_target.centroid.x**2 +
                self.current_target.centroid.y**2
            )

            if distance_to_goal < self.goal_tolerance:
                self.get_logger().info('Frontier reached, selecting next target')
                self.current_target = None
                self.select_next_frontier()

        if not self.frontiers and self.current_target is None:
            self.exploration_complete = True
            self.get_logger().info('Exploration complete - no more frontiers')

    def get_exploration_status(self):
        status = TaskInfo()
        status.id = 'exploration_task'
        status.task_type = 'explore'
        status.status = 'completed' if self.exploration_complete else 'in_progress'
        status.target_position = self.current_target.centroid if self.current_target else Point()
        return status


def main(args=None):
    rclpy.init(args=args)
    node = ExplorationCoordinatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()