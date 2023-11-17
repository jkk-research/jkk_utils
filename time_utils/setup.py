import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'time_utils'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*launch.[pxy][yma]*')),        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='he',
    maintainer_email='h@gmail.com',
    description='ROS 2 package for simple functions as human readable display, difference etc',
    license='GPL-3.0 license - GNU GENERAL PUBLIC LICENSE',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'display_time = time_utils.display_time:main',
            'display_time_once = time_utils.display_time_once:main'
        ],
    },
)
