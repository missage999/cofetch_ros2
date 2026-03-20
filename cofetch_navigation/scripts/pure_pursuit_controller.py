#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from cofetch_msgs.msg import NavStatus
import numpy as np


class PurePursuitController(Node):
    def __init__(self):
        super().__init__('pure_pursuit_controller')
        self.declare_parameter('lookahead_distance', 0.5)
        self.declare_parameter('target_velocity', 0.3)
        self.declare_parameter('max_angular_velocity', 1.5)
        self.declare_parameter('goal_tolerance', 0.1)

        self.lookahead_distance = self.get_parameter('lookahead_distance').value
        self.target_velocity = self.get_parameter('target_velocity').value
        self.max_angular_velocity = self.get_parameter('max_angular_velocity').value
        self.goal_tolerance = self.get_parameter('goal_tolerance').value

        self.current_pose = Pose()
        self.target_point = None
        self.path_points = []
        self.lookahead_point = None

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.target_sub = self.create_subscription(
            Point,
            '/navigation/target',
            self.target_callback,
            10
        )

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.status_pub = self.create_publisher(
            NavStatus,
            '/navigation/status',
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Pure Pursuit Controller started')

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    def target_callback(self, msg):
        self.target_point = msg
        self.path_points = [msg]
        self.get_logger().info(f'New target received: ({msg.x:.2f}, {msg.y:.2f})')

    def control_loop(self):
        if self.target_point is None or not self.path_points:
            self.publish_stop()
            return

        cmd = Twist()

        dx = self.target_point.x - self.current_pose.position.x
        dy = self.target_point.y - self.current_pose.position.y
        distance_to_goal = np.sqrt(dx*dx + dy*dy)

        current_angle = self.get_yaw_angle(self.current_pose.orientation)

        target_angle = np.arctan2(dy, dx)
        angle_diff = self.normalize_angle(target_angle - current_angle)

        if distance_to_goal < self.goal_tolerance:
            self.get_logger().info('Goal reached!')
            self.publish_stop()
            self.publish_status('goal_reached', distance_to_goal, 0.0)
            self.target_point = None
            return

        angular_correction = self.compute_pure_pursuit(angle_diff, distance_to_goal)

        cmd.linear.x = self.target_velocity if abs(angle_diff) < np.pi/4 else self.target_velocity * 0.5
        cmd.angular.z = np.clip(angular_correction, -self.max_angular_velocity, self.max_angular_velocity)

        self.cmd_vel_pub.publish(cmd)
        self.publish_status('navigating', distance_to_goal, angle_diff)

    def compute_pure_pursuit(self, angle_error, distance):
        k_angular = 2.0
        angular_cmd = k_angular * angle_error
        return angular_cmd

    def get_yaw_angle(self, quat):
        siny_cosp = 2.0 * (quat.w * quat.z + quat.x * quat.y)
        cosy_cosp = 1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z)
        return np.arctan2(siny_cosp, cosy_cosp)

    def normalize_angle(self, angle):
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle

    def publish_stop(self):
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)

    def publish_status(self, status, distance_to_goal, angle_to_goal):
        msg = NavStatus()
        msg.robot_name = 'robot1'
        msg.status = status
        msg.current_position = self.current_pose
        msg.target_position = Pose(position=self.target_point)
        msg.distance_to_goal = distance_to_goal
        msg.angle_to_goal = angle_to_goal
        self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PurePursuitController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()