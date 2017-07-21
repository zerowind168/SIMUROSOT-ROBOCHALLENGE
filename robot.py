# coding=utf-8
from math import radians

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import re


class Robot:
    def __init__(self):
        # 初始化
        rospy.init_node('turtlebot_robot', anonymous=False)

        rospy.loginfo("Press ctrl+c to stop!")
        rospy.on_shutdown(self.__shutdown)

        # 控制turtlebot运动

        self.__cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)

        # 一秒钟可以发10个指令
        # 让用户传入要运行多少秒
        self.rate = rospy.Rate(10)

        # 设置默认的转动角速度
        self.turn_cmd = Twist()
        self.turn_cmd.linear.x = 0
        # 转动角速度10度/秒
        self.turn_cmd.angular.z = radians(10)

        # 设置默认的运动速度
        self.move_cmd = Twist()
        self.move_cmd.angular.z = radians(0)
        # 直线速度0.1米/秒
        self.move_cmd.linear.x = 0.1

        # 获取turtlebot的图像
        self.bridge = CvBridge()
        self.image_received = False

        self.image_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.__recv_image)
        self.image = None
        # 获取初始障碍物位置信息
        self.state_sub = rospy.Subscriber("/gazebo/model_states", ModelStates, self.__recv_states)
        self.box_pos = []
        rospy.sleep(1)

    def set_move_speed(self, met_per_sec):
        """
        设置turtlebot的运动速度
        :param speed:float
        """
        self.move_cmd.angular.z = 0
        self.move_cmd.linear.x = met_per_sec

    def set_turn_speed(self, deg_per_sec):
        """
        设置turtlebot的转动速度
        :param deg_per_sec:int
        """
        self.turn_cmd.linear.x = 0
        self.turn_cmd.angular.z = radians(deg_per_sec)

    def go_forward(self, seconds):
        """
        让turtlebot向前走seconds秒
        :param seconds:int
        """
        times = seconds * 10
        for x in xrange(0, times):
            self.publish_twist(self.move_cmd)
            self.rate.sleep()
        rospy.sleep(1)

    def turn_around(self, seconds):
        """
        让turtlebot转动seconds秒
        :param seconds:int
        """
        times = seconds * 10
        for x in xrange(0, times):
            self.publish_twist(self.turn_cmd)
            self.rate.sleep()
        rospy.sleep(1)

    def publish_twist(self, twist):
        """
        发布twist指令
        :param twist:
        :return:
        """
        self.__cmd_vel.publish(twist)

    def get_image(self):
        """
        获取turtlebot当前看到的图像
        :return:image
        """
        return self.image

    def __recv_image(self, data):
        """
        将图像转换为OpenCV的格式并保存
        :param data:
        """
        cv_image = None
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")

        except CvBridgeError as e:
            print(e)
        self.image_received = True
        self.image = cv_image
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        ret, self.binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

    def get_box_position(self):
        """
        获取障碍箱子的位置，如：[(4.0, 0.655898), (4.0, -0.801722)]
        :return: 箱子坐标的列表
        """
        return self.box_pos

    def __recv_states(self, model_states):
        reg = 'newbox*'
        nameRe = re.compile(reg)
        res = []
        for i in xrange(len(model_states.name)):
            if nameRe.match(model_states.name[i]):
                x = float(model_states.pose[i].position.x)
                y = float(model_states.pose[i].position.y)
                res.append((x, y))
        self.box_pos = res
        pass

    def __shutdown(self):
        rospy.loginfo("Stop the turtlebot")
        self.__cmd_vel.publish(Twist())
        rospy.sleep(1)
