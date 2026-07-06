from glob import glob

from setuptools import setup

package_name = 'bot_mobile_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/web', glob('web/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Khalid Hago',
    maintainer_email='khalid.hago82@gmail.com',
    description='Phone teleoperation bridge for the bot mobile robot.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'web_server = bot_mobile_bridge.web_server:main',
        ],
    },
)
