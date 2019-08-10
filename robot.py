# coding=utf-8
from math import radians

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import re
from robot_cli import robot_cli


class Robot:
    def __init__(self):
        #rospy.init_node('turtlebot_robot', anonymous=False)
        self.my_robot=robot_cli("127.0.0.1")

        #rospy.loginfo("Press ctrl+c to stop!")
        #rospy.on_shutdown(self.__shutdown)

        # Control the movement of the turtlebot

        #self.__cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)


        self.rate = rospy.Rate(10)

 
        self.turn_cmd = Twist()
        self.turn_cmd.linear.x = 0
        self.turn_cmd.angular.z = radians(10)
        self.move_cmd = Twist()
        self.move_cmd.angular.z = radians(0)
        self.move_cmd.linear.x = 0.1

        
        # self.bridge = CvBridge()
        # self.image_received = False
        #
        # self.image_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.__recv_image)
        # self.image = None
        #
        # self.state_sub = rospy.Subscriber("/gazebo/model_states", ModelStates, self.__recv_states)
        # self.box_pos = []
        rospy.sleep(1)

    def set_move_speed(self, met_per_sec):
        """
        Set the speed of turtlebot
        :param speed:float
        """
        self.move_cmd.angular.z = 0
        self.move_cmd.linear.x = met_per_sec

    def set_turn_speed(self, deg_per_sec):
        """
        Set the rotation speed of the turtlebot
        :param deg_per_sec:int
        """
        self.turn_cmd.linear.x = 0
        self.turn_cmd.angular.z = radians(deg_per_sec)

    def go_forward(self, seconds):
        """
        :param seconds:int
        """
        times = seconds * 10
        for x in xrange(0, times):
            self.publish_twist(self.move_cmd)
            self.rate.sleep()
        rospy.sleep(1)

    def turn_around(self, seconds):
        """
        :param seconds:int
        """
        times = seconds * 10
        for x in xrange(0, times):
            self.publish_twist(self.turn_cmd)
            self.rate.sleep()
        rospy.sleep(1)

    def publish_twist(self, twist):
        """
        Publish twist
        :param twist:
        :return:
        """
        #self.__cmd_vel.publish(twist)
        self.my_robot.publish_twist(twist)

    def get_image(self):
        """
        Get the image that turtlebot is currently seeing
        :return:image
        """
        #return self.image
        return self.my_robot.get_image()

    def get_comImage(self):
        """
        :return:
        """
        return self.my_robot.get_comImage()


