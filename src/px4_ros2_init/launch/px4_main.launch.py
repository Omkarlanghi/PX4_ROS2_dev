import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_px4_ros2_init = get_package_share_directory('px4_ros2_init')

    # 1. Run the Core System in the ORIGINAL terminal
    core_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_px4_ros2_init, 'launch', 'px4_core.launch.py')
        )
    )

    # 2. Open a NEW terminal window for the Visualization System
    # This uses the default Ubuntu terminal (gnome-terminal)
    vis_launch = ExecuteProcess(
        cmd=['gnome-terminal', '--', 'ros2', 'launch', 'px4_ros2_init', 'px4_vis.launch.py'],
        output='screen'
    )

    return LaunchDescription([
        core_launch,
        vis_launch
    ])