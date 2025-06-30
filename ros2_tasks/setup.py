from setuptools import setup

package_name = 'ros2_tasks'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='dinith.22@cse.mrt.ac.lk',
    description='ROS 2 tasks solutions',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_re_pub = ros2_tasks.task1.pose_re_pub:main',
            'params_setter = ros2_tasks.task2.params_setter:main',
            'twist_from_database = ros2_tasks.task3.twist_from_database:main',
            'zero_twist = ros2_tasks.task4.zero_twist:main',
            'param_reader = ros2_tasks.task6.param_reader:main',
        ],
    },
)