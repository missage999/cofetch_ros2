#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, BoundingBox2D
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np
from collections import deque
import yaml
import os


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        self.declare_parameter('config_file', '')
        self.declare_parameter('camera_topic', '/color/preview/image')
        self.declare_parameter('enable_display', False)

        config_file = self.get_parameter('config_file').value
        self.camera_topic = self.get_parameter('camera_topic').value
        self.enable_display = self.get_parameter('enable_display').value

        self.bridge = CvBridge()
        self.detection_history = deque(maxlen=10)

        self.load_color_config(config_file)

        self.image_sub = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            10
        )

        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/detections',
            10
        )

        self.get_logger().info(f'Object Detection Node started, subscribing to {self.camera_topic}')

    def load_color_config(self, config_file):
        self.color_ranges = {
            'red': {'lower': np.array([0, 100, 100]), 'upper': np.array([10, 255, 255])},
            'green': {'lower': np.array([40, 100, 100]), 'upper': np.array([80, 255, 255])},
            'blue': {'lower': np.array([100, 100, 100]), 'upper': np.array([130, 255, 255])},
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'cofetch_ros2' in config and 'perception' in config['cofetch_ros2']:
                        colors = config['cofetch_ros2']['perception'].get('color_detection', {})
                        for color_name, ranges in colors.items():
                            if color_name in self.color_ranges:
                                self.color_ranges[color_name] = {
                                    'lower': np.array(ranges.get('hsv_lower', [0, 100, 100])),
                                    'upper': np.array(ranges.get('hsv_upper', [10, 255, 255]))
                                }
                self.get_logger().info(f'Loaded color config from {config_file}')
            except Exception as e:
                self.get_logger().warn(f'Failed to load config: {e}')

    def detect_color_objects(self, hsv, mask):
        detected_objects = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:
                continue

            M = cv2.moments(contour)
            if M['m00'] == 0:
                continue

            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            shape = self.identify_shape(contour)

            detected_objects.append({
                'center': (cx, cy),
                'area': area,
                'shape': shape,
                'contour': contour
            })

        return detected_objects

    def identify_shape(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        if len(approx) <= 6:
            area = cv2.contourArea(contour)
            circularity = 4 * np.pi * area / (peri * peri) if peri > 0 else 0

            if circularity > 0.75:
                return 'circle'

            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            if width > 0 and height > 0:
                aspect_ratio = min(width, height) / max(width, height)
                if aspect_ratio > 0.85:
                    return 'cylinder'

            return 'unknown'

        if len(approx) == 4:
            return 'box'
        elif len(approx) > 4:
            return 'sphere'

        return 'unknown'

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        all_detections = []

        for color_name, ranges in self.color_ranges.items():
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            objects = self.detect_color_objects(hsv, mask)

            for obj in objects:
                detection = {
                    'color': color_name,
                    'shape': obj['shape'],
                    'x': obj['center'][0],
                    'y': obj['center'][1],
                    'area': obj['area']
                }
                all_detections.append(detection)

                cv2.drawContours(cv_image, [obj['contour']], -1, (0, 255, 0), 2)
                label = f'{color_name}_{obj["shape"]}'
                cv2.putText(cv_image, label, obj['center'], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        self.detection_history.append(all_detections)

        detection_msg = Detection2DArray()
        for det in all_detections:
            det_2d = Detection2DArray()
            bbox = BoundingBox2D()
            bbox.center.position.x = float(det['x'])
            bbox.center.position.y = float(det['y'])
            det_2d.detections.append(bbox)

        if all_detections:
            self.detection_pub.publish(detection_msg)

        if self.enable_display:
            cv2.imshow('Object Detection', cv_image)
            cv2.waitKey(1)

        self.get_logger().debug(f'Detected {len(all_detections)} objects')


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()