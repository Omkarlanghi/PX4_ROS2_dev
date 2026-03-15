#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from px4_msgs.msg import VehicleOdometry
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from tf2_ros import TransformBroadcaster


class PX4VehicleOdometryRVizNode(Node):
    def __init__(self):
        super().__init__('px4_vehicle_odometry_rviz_node')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.world_frame = 'map'
        self.body_frame = 'base_link'
        self.max_path_length = 300

        self.pose_pub = self.create_publisher(PoseStamped, '/rviz/vehicle_odometry/pose', 10)
        self.path_pub = self.create_publisher(Path, '/rviz/vehicle_odometry/path', 10)
        self.odom_pub = self.create_publisher(Odometry, '/rviz/vehicle_odometry/odometry', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.path_msg = Path()
        self.path_msg.header.frame_id = self.world_frame

        self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.vehicle_odometry_callback,
            qos,
        )

        print('Vehicle odometry RViz node started')
        print('Subscribed to /fmu/out/vehicle_odometry')

    def vehicle_odometry_callback(self, msg):
        if not self._vector_is_finite(msg.position) or not self._quaternion_is_finite(msg.q):
            return

        position_enu, orientation_enu = self._ned_to_enu_pose(msg.position, msg.q)
        linear_velocity_enu = self._ned_to_enu_vector(msg.velocity)
        angular_velocity_enu = self._ned_to_enu_vector(msg.angular_velocity)

        pose_msg = self._create_pose_msg(position_enu, orientation_enu)
        odom_msg = self._create_odometry_msg(pose_msg, linear_velocity_enu, angular_velocity_enu)
        tf_msg = self._create_transform_msg(pose_msg)

        self.pose_pub.publish(pose_msg)
        self.odom_pub.publish(odom_msg)
        self.tf_broadcaster.sendTransform(tf_msg)

        self.path_msg.header.stamp = pose_msg.header.stamp
        self.path_msg.poses.append(pose_msg)
        if len(self.path_msg.poses) > self.max_path_length:
            self.path_msg.poses.pop(0)
        self.path_pub.publish(self.path_msg)

    def _ned_to_enu_pose(self, position_ned, quaternion_ned):
        position_enu = [
            float(position_ned[1]),
            float(position_ned[0]),
            float(-position_ned[2]),
        ]
        quaternion_enu = [
            float(quaternion_ned[2]),
            float(quaternion_ned[1]),
            float(-quaternion_ned[3]),
            float(quaternion_ned[0]),
        ]
        return position_enu, quaternion_enu

    def _ned_to_enu_vector(self, vector_ned):
        return [
            float(vector_ned[1]),
            float(vector_ned[0]),
            float(-vector_ned[2]),
        ]

    def _create_pose_msg(self, position_enu, orientation_enu):
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = self.world_frame
        pose_msg.pose.position.x = position_enu[0]
        pose_msg.pose.position.y = position_enu[1]
        pose_msg.pose.position.z = position_enu[2]
        pose_msg.pose.orientation.x = orientation_enu[0]
        pose_msg.pose.orientation.y = orientation_enu[1]
        pose_msg.pose.orientation.z = orientation_enu[2]
        pose_msg.pose.orientation.w = orientation_enu[3]
        return pose_msg

    def _create_odometry_msg(self, pose_msg, linear_velocity_enu, angular_velocity_enu):
        odom_msg = Odometry()
        odom_msg.header = pose_msg.header
        odom_msg.child_frame_id = self.body_frame
        odom_msg.pose.pose = pose_msg.pose
        odom_msg.twist.twist.linear.x = linear_velocity_enu[0]
        odom_msg.twist.twist.linear.y = linear_velocity_enu[1]
        odom_msg.twist.twist.linear.z = linear_velocity_enu[2]
        odom_msg.twist.twist.angular.x = angular_velocity_enu[0]
        odom_msg.twist.twist.angular.y = angular_velocity_enu[1]
        odom_msg.twist.twist.angular.z = angular_velocity_enu[2]
        return odom_msg

    def _create_transform_msg(self, pose_msg):
        tf_msg = TransformStamped()
        tf_msg.header = pose_msg.header
        tf_msg.child_frame_id = self.body_frame
        tf_msg.transform.translation.x = pose_msg.pose.position.x
        tf_msg.transform.translation.y = pose_msg.pose.position.y
        tf_msg.transform.translation.z = pose_msg.pose.position.z
        tf_msg.transform.rotation = pose_msg.pose.orientation
        return tf_msg

    def _vector_is_finite(self, values):
        return all(math.isfinite(value) for value in values[:3])

    def _quaternion_is_finite(self, values):
        return all(math.isfinite(value) for value in values[:4])


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PX4VehicleOdometryRVizNode())
    rclpy.shutdown()


if __name__ == '__main__':
    main()
