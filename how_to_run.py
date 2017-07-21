import math

import rospy
from geometry_msgs.msg import Twist


def Run(robot):
    # robot.set_move_speed(1)
    # robot.go_forward(1)

    print robot.get_box_position()

    twist = Twist()
    twist.linear.x = 2
    twist.angular.z = math.radians(30)
    rate = rospy.Rate(20)
    for _ in xrange(20):
        robot.publish_twist(twist)
        rate.sleep()
