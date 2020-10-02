# coding=utf-8
from socket import *
import cStringIO
from geometry_msgs.msg import Twist, genpy
from gazebo_msgs.msg import ModelStates
from sensor_msgs.msg import CompressedImage,Image
from rosgraph_msgs.msg import Clock
import rospy
from cv_bridge import CvBridge, CvBridgeError
import struct


class robot_cli:
    def __init__(self,host,port=7777):

        rospy.init_node('robot', anonymous=False)
        self.bridge = CvBridge()
        self.tcpCliSock = socket(AF_INET, SOCK_STREAM)
        addr = (host, port)
        self.tcpCliSock.connect(addr)
        print "The connection is successful"

        self.comImage = CompressedImage()
        self.image=Image()
        self.time = Clock()
        self.box_pos = ModelStates()
        self.isEnd=False

    def get_comImage(self):
        """
        :return:
        """
        if not self.isEnd:
            message=b"cim"
            try:
                self.tcpCliSock.send(message)
                flag= self.tcpCliSock.recv(4)
                length=struct.unpack('i',flag)[0]
                data=""
                while len(data)<length:
                    data+=self.tcpCliSock.recv(length)
                try:
                    self.comImage.deserialize(data)
                    cv_image = None
                    try:
                        cv_image = self.bridge.compressed_imgmsg_to_cv2(self.comImage, "bgr8")
                    except CvBridgeError as e:
                        print(e)
                    return cv_image
                except genpy.DeserializationError:
                    print rospy.loginfo("deserialize comImage failed!")
            except Exception,msg:
                print msg
                self.isEnd=True

    def get_image(self):
        """
        :return:
        """
        if not self.isEnd:
            message=b"img"
            try:
                self.tcpCliSock.send(message)
                data=""
                while len(data)<921667:
                    data+=self.tcpCliSock.recv(921667)
                try:
                    self.image.deserialize(data)
                    cv_image = None
                    try:
                        cv_image = self.bridge.imgmsg_to_cv2(self.image, "bgr8")
                    except CvBridgeError as e:
                        print(e)
                    return cv_image
                except genpy.DeserializationError:
                    print rospy.loginfo("deserialize image failed!")
            except Exception,msg:
                print msg
                self.isEnd=True

    def get_box_pos(self):
         """
         :return:
         """
         if not self.isEnd:
             try:
                 message = b"box"
                 self.tcpCliSock.send(message)
                 flag=self.tcpCliSock.recv(4)
                 length=struct.unpack('i',flag)[0]
                 data=""
                 while len(data)<length:
                     data+=self.tcpCliSock.recv(length)
                 try:
                     self.box_pos.deserialize(data)
                     return self.box_pos
                 except genpy.DeserializationError:
                     print rospy.loginfo("deserialize box_pos failed!")
             except Exception,msg:
                 print msg
                 self.isEnd = True

    def get_time(self):
        """
        Get the time of the platform
        :return:
        """
        if not self.isEnd:
            try:
                message = b"tim"
                self.tcpCliSock.send(message)
                data = self.tcpCliSock.recv(8)
                try:
                    self.time.deserialize(data)
                    return self.time
                except genpy.DeserializationError:
                    print rospy.loginfo("deserialize time failed!")
            except Exception,msg:
                print msg
                self.isEnd = True

    def publish_twist(self, twist):
        """
        Send commands to the robot and control the movement of the robot
        :param twist:
        :return:
        """
        buff = cStringIO.StringIO()
        twist.serialize(buff)
        message=b"tws"
        self.tcpCliSock.sendall(message+buff.getvalue())

    def end(self):
        message=b"end"
        self.tcpCliSock.send(message)

    def __del__(self):
        self.end()
        self.tcpCliSock.close()

