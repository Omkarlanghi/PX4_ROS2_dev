import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    rviz_config = os.path.join(
        get_package_share_directory('px4_ros2_init'),
        'rviz',
        'rviz.rviz'
    )

    return LaunchDescription([
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
        Node(
            package='px4_ros2_init',
            executable='vehicle_odometry_viz_node',
            name='vehicle_odometry_viz_node',
            output='screen'
        ),
    ])
