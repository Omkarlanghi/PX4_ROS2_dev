#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import TrajectorySetpoint, VehicleCommand

class PX4CommandNode(Node):
    def __init__(self):
        super().__init__('px4_command_node')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Publishers
        self.setpoint_publisher = self.create_publisher(
            TrajectorySetpoint, 
            '/fmu/in/trajectory_setpoint', 
            qos)
            
        self.command_publisher = self.create_publisher(
            VehicleCommand, 
            '/fmu/in/vehicle_command', 
            qos)

        # 10Hz Timer
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.offboard_setpoint_counter = 0

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        """Helper function to send VehicleCommands to PX4"""
        msg = VehicleCommand()
        msg.param1 = float(param1)
        msg.param2 = float(param2)
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.command_publisher.publish(msg)

    def timer_callback(self):
        # 1. Constantly Publish the Trajectory Setpoint
        # PX4 uses NED coordinates: North, East, Down. 
        # To fly 50 meters UP, the Z value must be -50.0.
        setpoint_msg = TrajectorySetpoint()
        setpoint_msg.position = [0.0, 0.0, -50.0]
        setpoint_msg.yaw = 0.0 # Face North
        setpoint_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.setpoint_publisher.publish(setpoint_msg)

        # 2. Wait 1 second, then Arm and switch to Offboard
        if self.offboard_setpoint_counter == 10:
            # Switch to Offboard Mode (PX4 Custom Mode: 6)
            self.publish_vehicle_command(
                VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 
                param1=1.0, 
                param2=6.0
            )
            self.get_logger().info("Commanding Offboard Mode...")

            # Arm the Drone
            self.publish_vehicle_command(
                VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 
                param1=1.0
            )
            self.get_logger().info("Commanding Arming... Taking off to 50m!")

        # Stop counting once we pass 10 to prevent spamming the commands
        if self.offboard_setpoint_counter <= 10:
            self.offboard_setpoint_counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = PX4CommandNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
