# coding=utf-8
import rospy
from socket import *

import time
from rosgraph_msgs.msg import Clock, genpy


class ClockReceiver:
    def __init__(self,host,port=8888):
        rospy.init_node('clock_receiver', anonymous=False)
        rospy.on_shutdown(self.__shutdown)
        if rospy.has_param("use_sim_time"):
            # print "use_sim_time: {}".format(rospy.get_param("use_sim_time"))
            rospy.delete_param("use_sim_time")
        rospy.set_param("use_sim_time", 1)

        self.time_tcpCliSock = socket(AF_INET, SOCK_STREAM)

        addr = (host, port)
        self.time_tcpCliSock.connect(addr)
        print "time_tcp连接成功"

        # clock pub
        self.clock_pub = rospy.Publisher("clock", Clock, queue_size=1000)
        self.clock = Clock()

        self.isStop = False

    def run(self):
        while not self.isStop:
            try:
                data = self.time_tcpCliSock.recv(8)
            except Exception,msg:
                print msg
                continue
            try:
                self.clock.deserialize(data)
                self.clock_pub.publish(self.clock)
            except genpy.DeserializationError:
                print rospy.loginfo("deserialize time failed!")

    def __shutdown(self):
        rospy.loginfo("clock topic is shutting down")
        self.isStop = True
        time.sleep(1)
        self.time_tcpCliSock.close()

    def __del__(self):
        self.time_tcpCliSock.close()


if __name__ == '__main__':
    clock_receiver = ClockReceiver("127.0.0.1")
    clock_receiver.run()
    rospy.spin()
