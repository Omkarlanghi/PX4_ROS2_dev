#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode

class PX4HeartbeatNode(Node):
    def __init__(self):
        super().__init__('px4_heartbeat_node')
        
        # Modular Control Flags: Toggle these depending on what your future Command Node will send
        self.control_position = True
        self.control_velocity = False
        self.control_acceleration = False

        self.publisher = self.create_publisher(
            OffboardControlMode, 
            '/fmu/in/offboard_control_mode', 
            10)
        
        # 10Hz timer required by PX4 to maintain Offboard Mode
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = OffboardControlMode()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.position = self.control_position
        msg.velocity = self.control_velocity
        msg.acceleration = self.control_acceleration
        msg.attitude = False
        msg.body_rate = False
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PX4HeartbeatNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()