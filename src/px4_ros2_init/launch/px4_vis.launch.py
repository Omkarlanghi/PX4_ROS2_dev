from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Start RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        ),

        # 2. Start your custom Visualizer Node
        Node(
            package='px4_ros2_init',
            executable='visualizer_node',
            name='px4_visualizer',
            output='screen'
        )
    ])