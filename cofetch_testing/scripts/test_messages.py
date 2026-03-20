#!/usr/bin/env python3

import unittest
import rclpy
from geometry_msgs.msg import Point


class TestCofetchMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def test_object_info_creation(self):
        from cofetch_msgs.msg import ObjectInfo
        obj = ObjectInfo()
        obj.id = 'test_001'
        obj.color = 'red'
        obj.shape = 'box'
        obj.position = Point(x=1.0, y=2.0, z=0.5)
        obj.size = 0.1
        obj.confidence = 0.95
        obj.is_grasped = False

        self.assertEqual(obj.id, 'test_001')
        self.assertEqual(obj.color, 'red')
        self.assertEqual(obj.shape, 'box')
        self.assertEqual(obj.position.x, 1.0)
        self.assertFalse(obj.is_grasped)

    def test_robot_status_creation(self):
        from cofetch_msgs.msg import RobotStatus
        from geometry_msgs.msg import Quaternion

        robot = RobotStatus()
        robot.id = 'robot_001'
        robot.position = Point(x=0.0, y=0.0, z=0.0)
        robot.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        robot.current_task_id = ''
        robot.battery_level = 0.8
        robot.status = 'idle'

        self.assertEqual(robot.id, 'robot_001')
        self.assertEqual(robot.battery_level, 0.8)
        self.assertEqual(robot.status, 'idle')

    def test_task_info_creation(self):
        from cofetch_msgs.msg import TaskInfo

        task = TaskInfo()
        task.id = 'task_001'
        task.task_type = 'pick_and_place'
        task.object_id = 'obj_001'
        task.object_color = 'red'
        task.target_position = Point(x=5.0, y=5.0, z=0.0)
        task.priority = 1.0
        task.status = 'pending'
        task.assigned_robot = ''

        self.assertEqual(task.id, 'task_001')
        self.assertEqual(task.task_type, 'pick_and_place')
        self.assertEqual(task.status, 'pending')


def main():
    unittest.main()


if __name__ == '__main__':
    main()