from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
            name='micro_xrce_agent',
            output='screen'
        ),
        ExecuteProcess(
            cmd=['bash', '-lc', 'cd ~/PX4-Autopilot && make px4_sitl gz_x500'],
            name='px4_sitl',
            output='screen'
        ),
        ExecuteProcess(
            cmd=['bash', '-lc', 'cd ~/Downloads && ./QGroundControl.AppImage'],
            name='qgroundcontrol',
            output='screen'
        ),
    ])
