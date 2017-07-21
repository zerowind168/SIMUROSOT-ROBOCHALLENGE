# coding=utf-8
import subprocess
import os
import sys

import rospy

from robot import Robot
import time
import how_to_run

if __name__ == '__main__':
    ScriptPath = os.path.split(os.path.realpath(sys.argv[0]))[0]
    # 启动gazebo
    roslaunch = ['roslaunch',
                 'turtlebot_gazebo',
                 'turtlebot_world.launch',
                 ('world_file:=' + ScriptPath + '/world/world'+sys.argv[1]+'-'+sys.argv[2])
                 ]

    p_roslaunch = subprocess.Popen(roslaunch)
    # 等待启动完成
    time.sleep(5)

    # 启动可视化界面
    rosrun = ['rosrun',
              'image_view',
              'image_view',
              'image:=/camera/rgb/image_raw'
              ]
    p_rosrun = subprocess.Popen(rosrun)
    time.sleep(2)

    # 运行函数
    robot = Robot()
    how_to_run.Run(robot)

    rospy.spin()
    sys.exit(0)
