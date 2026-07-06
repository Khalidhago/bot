from glob import glob

from setuptools import setup

package_name = 'bot_base'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Khalid Hago',
    maintainer_email='khalid.hago82@gmail.com',
    description='Differential-drive base controller for the bot mobile robot.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'base_node = bot_base.base_node:main',
        ],
    },
)
