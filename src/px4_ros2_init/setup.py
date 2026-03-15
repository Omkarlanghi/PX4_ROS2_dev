from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'px4_ros2_init'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Updated to strictly look for .launch.py files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='deadnote',
    maintainer_email='deadnote@todo.todo',
    description='PX4 ROS 2 Initialization, Control, and Visualization Environment',     license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'heartbeat_node = px4_ros2_init.px4_heartbeat_node:main',
            'visualizer_node = px4_ros2_init.px4_visualizer_node:main',
            'vehicle_odometry_rviz_node = px4_ros2_init.px4_vehicle_odometry_rviz_node:main',
        ],
    },
)
