from glob import glob

from setuptools import setup

package_name = 'uav_telemetry'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Khalid Hago',
    maintainer_email='khalid.hago82@gmail.com',
    description='MAVLink to ROS 2 telemetry bridge for PX4/ArduPilot flight controllers.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mavlink_bridge = uav_telemetry.mavlink_bridge:main',
        ],
    },
)
