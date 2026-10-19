from setuptools import find_packages, setup

package_name = 'workspace_health'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='horverno',
    maintainer_email='herno@ga.sze.hu',
    description='CustomTkinter GUI showing the git status of the GitHub repos in a workspace',
    license='GPL-3.0-only',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'workspace_health = workspace_health.main:main',
        ],
    },
)
