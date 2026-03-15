import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Start Micro XRCE-DDS Agent in a NEW terminal
        ExecuteProcess(
            cmd=['gnome-terminal', '--', 'MicroXRCEAgent', 'udp4', '-p', '8888'],
            output='screen'
        ),

        # 2. Start PX4 SITL Simulation (Gazebo) in a NEW terminal
        # We use bash to change directories first, and 'exec bash' keeps the window open if it crashes
        ExecuteProcess(
            cmd=['gnome-terminal', '--', 'bash', '-c', 'cd ~/PX4-Autopilot && make px4_sitl gz_x500; exec bash'],
            output='screen'
        ),

        # 3. Start the Heartbeat Node in the ORIGINAL terminal
        Node(
            package='px4_ros2_init',
            executable='heartbeat_node',
            name='px4_heartbeat_node',
            output='screen'
        )
    ])