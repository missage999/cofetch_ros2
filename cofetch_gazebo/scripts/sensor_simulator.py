#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, Imu
from nav_msgs.msg import Odometry
import math


class SensorSimulator(Node):
    def __init__(self):
        super().__init__('sensor_simulator')
        self.declare_parameter('use_sim_time', True)

        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        self.imu_pub = self.create_publisher(Imu, '/imu', 10)

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info('Sensor Simulator Started')

    def timer_callback(self):
        scan_msg = LaserScan()
        scan_msg.header.stamp = self.get_clock().now().to_msg()
        scan_msg.header.frame_id = 'rplidar_link'
        scan_msg.angle_min = -math.pi
        scan_msg.angle_max = math.pi
        scan_msg.angle_increment = math.pi / 180
        scan_msg.time_increment = 0.001
        scan_msg.scan_time = 0.1
        scan_msg.range_min = 0.12
        scan_msg.range_max = 12.0
        scan_msg.ranges = [12.0] * 360

        self.scan_pub.publish(scan_msg)

        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = 'imu_link'
        imu_msg.orientation.w = 1.0
        imu_msg.angular_velocity_covariance = [0.0] * 9
        imu_msg.linear_acceleration_covariance = [0.0] * 9

        self.imu_pub.publish(imu_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SensorSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()