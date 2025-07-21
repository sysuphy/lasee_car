from setuptools import setup

package_name = 'sticker_tracker_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/tracker.launch.py']),
    ],
    install_requires=['setuptools', 'opencv-python', 'pyserial'],
    zip_safe=True,
    maintainer='zhugeliang',
    maintainer_email='your@email.com',
    description='A simple sticker tracker node',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 指向实际有功能的节点文件
            'sticker_tracker_node = sticker_tracker_pkg.sticker_tracker_node:main',
            # 保留原tracker_node（如果需要）
            'tracker_node = sticker_tracker_pkg.tracker_node:main'
        ],
    }
)
