#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Pose, Point, Quaternion
from nav_msgs.msg import OccupancyGrid, Path
from cofetch_msgs.msg import FrontierInfo
import numpy as np
from collections import deque


class FrontierDetectionNode(Node):
    def __init__(self):
        super().__init__('frontier_detection_node')
        self.declare_parameter('map_resolution', 0.05)
        self.declare_parameter('map_width', 400)
        self.declare_parameter('map_height', 400)
        self.declare_parameter('min_frontier_size', 5)
        self.declare_parameter('robot_frame', 'base_link')

        self.map_resolution = self.get_parameter('map_resolution').value
        self.map_width = self.get_parameter('map_width').value
        self.map_height = self.get_parameter('map_height').value
        self.min_frontier_size = self.get_parameter('min_frontier_size').value
        self.robot_frame = self.get_parameter('robot_frame').value

        self.map_data = np.full((self.map_height, self.map_width), -1, dtype=np.int8)
        self.robot_position = (self.map_width // 2, self.map_height // 2)

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.frontier_pub = self.create_publisher(
            FrontierInfo,
            '/frontiers',
            10
        )

        self.map_pub = self.create_publisher(
            OccupancyGrid,
            '/map',
            10
        )

        self.timer = self.create_timer(1.0, self.publish_frontiers)

        self.get_logger().info('Frontier Detection Node started')

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))

        self.robot_position = (self.map_width // 2, self.map_height // 2)

        for i, r in enumerate(ranges):
            if np.isinf(r) or r > msg.range_max or r < msg.range_min:
                continue

            angle = angles[i]
            x = int(r * np.cos(angle) / self.map_resolution) + self.robot_position[0]
            y = int(r * np.sin(angle) / self.map_resolution) + self.robot_position[1]

            if 0 <= x < self.map_width and 0 <= y < self.map_height:
                self.map_data[y, x] = 100

        for dx in range(-5, 6):
            for dy in range(-5, 6):
                nx = self.robot_position[0] + dx
                ny = self.robot_position[1] + dy
                if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                    if self.map_data[ny, nx] != 100:
                        self.map_data[ny, nx] = 0

    def find_frontiers(self):
        frontiers = []
        visited = np.zeros_like(self.map_data, dtype=bool)

        for y in range(1, self.map_height - 1):
            for x in range(1, self.map_width - 1):
                if self.map_data[y, x] == -1 and not visited[y, x]:
                    if self.has_free_neighbor(x, y):
                        frontier_points = self.bfs_frontier(x, y, visited)
                        if len(frontier_points) >= self.min_frontier_size:
                            centroid_x = np.mean([p[0] for p in frontier_points])
                            centroid_y = np.mean([p[1] for p in frontier_points])
                            frontiers.append({
                                'points': frontier_points,
                                'centroid': (centroid_x, centroid_y),
                                'size': len(frontier_points)
                            })

        return frontiers

    def has_free_neighbor(self, x, y):
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                if self.map_data[ny, nx] == 0:
                    return True
        return False

    def bfs_frontier(self, start_x, start_y, visited):
        queue = [(start_x, start_y)]
        points = []

        while queue:
            x, y = queue.pop(0)
            if visited[y, x]:
                continue
            visited[y, x] = True

            if self.map_data[y, x] == -1:
                points.append((x, y))

                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                        if not visited[ny, nx]:
                            queue.append((nx, ny))

        return points

    def publish_frontiers(self):
        frontiers = self.find_frontiers()

        grid_msg = OccupancyGrid()
        grid_msg.header.stamp = self.get_clock().now().to_msg()
        grid_msg.header.frame_id = 'map'
        grid_msg.info.resolution = self.map_resolution
        grid_msg.info.width = self.map_width
        grid_msg.info.height = self.map_height
        grid_msg.data = self.map_data.flatten().tolist()
        self.map_pub.publish(grid_msg)

        for frontier in frontiers:
            frontier_msg = FrontierInfo()
            frontier_msg.robot_name = 'robot1'
            frontier_msg.centroid = Point(
                x=float(frontier['centroid'][0]) * self.map_resolution,
                y=float(frontier['centroid'][1]) * self.map_resolution,
                z=0.0
            )
            frontier_msg.size = float(frontier['size'])
            frontier_msg.value = float(frontier['size']) * 1.0
            frontier_msg.is_assigned = False
            self.frontier_pub.publish(frontier_msg)

        self.get_logger().debug(f'Published {len(frontiers)} frontiers')


def main(args=None):
    rclpy.init(args=args)
    node = FrontierDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()