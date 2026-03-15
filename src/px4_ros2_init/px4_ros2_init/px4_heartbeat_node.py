#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode

class PX4HeartbeatNode(Node):
    def __init__(self):
        super().__init__('px4_heartbeat_node')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Modular Control Flags: Toggle these depending on what your future Command Node will send
        self.control_position = True
        self.control_velocity = False
        self.control_acceleration = False

        self.publisher = self.create_publisher(
            OffboardControlMode, 
            '/fmu/in/offboard_control_mode', 
            qos)
        
        # 10Hz timer required by PX4 to maintain Offboard Mode
        self.heartbeat_frequency_hz = 10.0
        self.print_every_n_messages = 10
        self.publish_count = 0

        self.timer = self.create_timer(1.0 / self.heartbeat_frequency_hz, self.timer_callback)
        print('Heart node started')
        print(f'Heartbeat sending at {self.heartbeat_frequency_hz} Hz')
        print(f'Heartbeat print message shown every {self.print_every_n_messages} messages')

    def timer_callback(self):
        msg = OffboardControlMode()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.position = self.control_position
        msg.velocity = self.control_velocity
        msg.acceleration = self.control_acceleration
        msg.attitude = False
        msg.body_rate = False
        self.publisher.publish(msg)
        self.publish_count += 1

        if self.publish_count % self.print_every_n_messages == 0:
            print(f'Heartbeat sent at {self.heartbeat_frequency_hz} Hz')

def main(args=None):
    rclpy.init(args=args)
    node = PX4HeartbeatNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
