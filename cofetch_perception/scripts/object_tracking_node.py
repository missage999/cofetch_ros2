#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Header
from cofetch_msgs.msg import ObjectInfo, ObjectList
import cv2
import numpy as np
from collections import deque


class ObjectTrackingNode(Node):
    def __init__(self):
        super().__init__('object_tracking_node')
        self.declare_parameter('max_tracking_distance', 50.0)
        self.declare_parameter('tracking_timeout', 5.0)

        self.max_tracking_distance = self.get_parameter('max_tracking_distance').value
        self.tracking_timeout = self.get_parameter('tracking_timeout').value

        self.tracked_objects = {}
        self.next_object_id = 1
        self.last_update_time = {}

        self.detection_sub = None
        self.image_sub = None

        self.object_list_pub = self.create_publisher(
            ObjectList,
            '/objects',
            10
        )

        self.timer = self.create_timer(1.0, self.publish_object_list)

        self.get_logger().info('Object Tracking Node started')

    def update_tracked_objects(self, detections, header):
        current_time = self.get_clock().now()

        for det in detections:
            matched_id = None
            min_distance = float('inf')

            for obj_id, obj_data in self.tracked_objects.items():
                distance = np.sqrt(
                    (det['x'] - obj_data['x'])**2 +
                    (det['y'] - obj_data['y'])**2
                )

                if distance < min_distance and distance < self.max_tracking_distance:
                    min_distance = distance
                    matched_id = obj_id

            if matched_id is not None:
                self.tracked_objects[matched_id] = {
                    'x': det['x'],
                    'y': det['y'],
                    'color': det['color'],
                    'shape': det['shape'],
                    'area': det.get('area', 0)
                }
                self.last_update_time[matched_id] = current_time
            else:
                new_id = f'obj_{self.next_object_id}'
                self.next_object_id += 1
                self.tracked_objects[new_id] = {
                    'x': det['x'],
                    'y': det['y'],
                    'color': det['color'],
                    'shape': det['shape'],
                    'area': det.get('area', 0)
                }
                self.last_update_time[new_id] = current_time

        objects_to_remove = []
        for obj_id in self.tracked_objects.keys():
            if obj_id in self.last_update_time:
                time_diff = (current_time - self.last_update_time[obj_id]).nanoseconds / 1e9
                if time_diff > self.tracking_timeout:
                    objects_to_remove.append(obj_id)

        for obj_id in objects_to_remove:
            del self.tracked_objects[obj_id]
            del self.last_update_time[obj_id]

    def publish_object_list(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'camera_frame'

        object_list_msg = ObjectList()
        object_list_msg.header = header

        for obj_id, obj_data in self.tracked_objects.items():
            obj_info = ObjectInfo()
            obj_info.id = obj_id
            obj_info.color = obj_data['color']
            obj_info.shape = obj_data['shape']
            obj_info.position = Point(
                x=float(obj_data['x']) / 640.0,
                y=float(obj_data['y']) / 480.0,
                z=0.0
            )
            obj_info.size = float(obj_data['area']) / 1000.0
            obj_info.confidence = 0.8
            obj_info.is_grasped = False

            object_list_msg.objects.append(obj_info)

        if object_list_msg.objects:
            self.object_list_pub.publish(object_list_msg)
            self.get_logger().debug(f'Published {len(object_list_msg.objects)} tracked objects')


def main(args=None):
    rclpy.init(args=args)
    node = ObjectTrackingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()