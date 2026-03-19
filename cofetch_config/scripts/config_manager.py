#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import GetParameters, SetParameters
from rclpy.parameter import Parameter
from ament_index_python.packages import get_package_share_directory
import yaml
import os


class ConfigManager(Node):
    def __init__(self):
        super().__init__('config_manager')
        self.declare_parameter('config_dir', '')

        config_dir = self.get_parameter('config_dir').value
        if not config_dir:
            pkg_dir = get_package_share_directory('cofetch_config')
            config_dir = os.path.join(pkg_dir, 'config')

        self.configs = {}
        self.load_all_configs(config_dir)

        self.get_logger().info(f'Config Manager started with {len(self.configs)} config files')

        self.get_service = self.create_service(
            GetParameters, 'config/get', self.get_config_callback)

        self.set_service = self.create_service(
            SetParameters, 'config/set', self.set_config_callback)

    def load_all_configs(self, config_dir):
        if not os.path.exists(config_dir):
            self.get_logger().warn(f'Config directory not found: {config_dir}')
            return

        for filename in os.listdir(config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(config_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        config_name = os.path.splitext(filename)[0]
                        self.configs[config_name] = yaml.safe_load(f)
                        self.get_logger().info(f'Loaded config: {config_name}')
                except Exception as e:
                    self.get_logger().error(f'Failed to load {filename}: {e}')

    def get_config_callback(self, request, response):
        keys = request.names
        values = []

        for key in keys:
            parts = key.split('.')
            config = self.configs

            for part in parts:
                if isinstance(config, dict) and part in config:
                    config = config[part]
                else:
                    config = None
                    break

            if config is not None:
                param = Parameter(name=key, value=config)
                values.append(param.to_parameter_msg())
            else:
                param = Parameter(name=key, value=0)
                values.append(param.to_parameter_msg())

        response.values = values
        return response

    def set_config_callback(self, request, response):
        for param in request.parameters:
            self.get_logger().info(f'Parameter update request: {param.name} = {param.value}')

        response.successful = True
        response.reason = 'Parameters updated'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ConfigManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()