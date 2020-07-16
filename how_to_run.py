# coding=utf-8
import rospy
from geometry_msgs.msg import Twist
from math import radians
import cv2
from robot import Robot
def Run(robot):
    # Get image and save image
    image=robot.get_image()
    cv2.imwrite("image.jpg",image)
    # Get compressed image and save iamge  
    comImage=robot.get_comImage()
    cv2.imwrite("comImage.jpg",comImage)
    #Get obstacle coordinates and print the information
    #pos=robot.get_box_position()
    #print pos
    #Send commands to the robot
    rate=rospy.Rate(10)
    twist=Twist()
    twist.linear.x=1
    time=2*10
    for i in xrange(0,time):
        robot.publish_twist(twist)
        rate.sleep()

    twist.angular.z=radians(90)
    twist.linear.x=0
    time=1*10
    for i in xrange(0,time):
        robot.publish_twist(twist)
        rate.sleep()

if __name__ == '__main__':
    robot=Robot()
    Run(robot)
