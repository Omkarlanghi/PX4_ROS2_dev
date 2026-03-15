#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleOdometry, TrajectorySetpoint
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker

class PX4Visualizer(Node):
    def __init__(self):
        super().__init__('px4_visualizer')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # --- GROUP 1: PX4 RAW ODOMETRY (RED) ---
        self.raw_path = Path()
        self.raw_path.header.frame_id = "map"
        self.raw_pose_pub = self.create_publisher(PoseStamped, '/vis/raw_px4_pose', 10)
        self.raw_marker_pub = self.create_publisher(Marker, '/vis/raw_px4_marker', 10)
        self.create_subscription(VehicleOdometry, '/fmu/out/vehicle_odometry', self.raw_odom_cb, qos)

        # --- GROUP 2: EXTERNAL SENSORS (Placeholder) ---
        self.sensor_pose_pub = self.create_publisher(PoseStamped, '/vis/sensor_pose', 10)

        # --- GROUP 3: FUSED ESTIMATION (BLUE - Placeholder) ---
        self.fused_path = Path()
        self.fused_path.header.frame_id = "map"
        self.fused_pose_pub = self.create_publisher(PoseStamped, '/vis/fused_pose', 10)
        self.fused_marker_pub = self.create_publisher(Marker, '/vis/fused_marker', 10)

        # --- GROUP 4: TRAJECTORY SETPOINT (GREEN) ---
        self.cmd_path = Path()
        self.cmd_path.header.frame_id = "map"
        self.cmd_pose_pub = self.create_publisher(PoseStamped, '/vis/command_pose', 10)
        self.cmd_marker_pub = self.create_publisher(Marker, '/vis/command_marker', 10)
        self.create_subscription(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', self.cmd_cb, qos)

    def ned_to_enu(self, pos, q):
        """Converts PX4 NED coordinates to ROS 2 ENU coordinates."""
        enu_pos = [pos[1], pos[0], -pos[2]]
        enu_q = [q[2], q[1], -q[3], q[0]]
        return enu_pos, enu_q

    def create_pose_msg(self, pos, q):
        p = PoseStamped()
        p.header.stamp = self.get_clock().now().to_msg()
        p.header.frame_id = "map"
        p.pose.position.x, p.pose.position.y, p.pose.position.z = float(pos[0]), float(pos[1]), float(pos[2])
        p.pose.orientation.x, p.pose.orientation.y, p.pose.orientation.z, p.pose.orientation.w = float(q[0]), float(q[1]), float(q[2]), float(q[3])
        return p

    def create_colored_line_marker(self, path_msg, ns, r, g, b):
        """Generates a LINE_STRIP marker to force RViz to draw the path in a specific color."""
        m = Marker()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = "map"
        m.ns = ns
        m.id = 0
        m.type = Marker.LINE_STRIP
        m.action = Marker.ADD
        m.scale.x = 0.05  # Controls the thickness of the line
        m.color.r = float(r)
        m.color.g = float(g)
        m.color.b = float(b)
        m.color.a = 1.0   # 1.0 is fully opaque
        
        # Populate the marker with points from the path
        for pose_stamped in path_msg.poses:
            pt = Point()
            pt.x = pose_stamped.pose.position.x
            pt.y = pose_stamped.pose.position.y
            pt.z = pose_stamped.pose.position.z
            m.points.append(pt)
        return m

    def raw_odom_cb(self, msg):
        p_enu, q_enu = self.ned_to_enu(msg.position, msg.q)
        pose = self.create_pose_msg(p_enu, q_enu)
        self.raw_pose_pub.publish(pose)
        
        self.raw_path.poses.append(pose)
        if len(self.raw_path.poses) > 200: self.raw_path.poses.pop(0)

        # Publish the Red Marker
        marker = self.create_colored_line_marker(self.raw_path, "raw_px4", 1.0, 0.0, 0.0)
        self.raw_marker_pub.publish(marker)

    def cmd_cb(self, msg):
        # Only process if position data is valid (not NaN)
        if not any(map(lambda x: x == float('nan'), msg.position)):
            p_enu = [msg.position[1], msg.position[0], -msg.position[2]]
            pose = self.create_pose_msg(p_enu, [0.0, 0.0, 0.0, 1.0])
            self.cmd_pose_pub.publish(pose)
            
            self.cmd_path.poses.append(pose)
            if len(self.cmd_path.poses) > 200: self.cmd_path.poses.pop(0)

            # Publish the Green Marker
            marker = self.create_colored_line_marker(self.cmd_path, "cmd_px4", 0.0, 1.0, 0.0)
            self.cmd_marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PX4Visualizer())
    rclpy.shutdown()

if __name__ == '__main__':
    main()