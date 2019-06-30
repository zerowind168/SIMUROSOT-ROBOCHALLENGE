# coding=utf-8
from socket import*
import rospy
from rosgraph_msgs.msg import Clock
import cStringIO

class GazeboTime:
    def __init__(self,port=8888):
        rospy.init_node('my_robot', anonymous=False)
        rospy.on_shutdown(self.__shutdown)
        # time tcp
        self.time_tcpSock = socket(AF_INET, SOCK_STREAM)
        self.time_connection = None
        self.time_tcpSock.bind(("", port))
        self.time_tcpSock.listen(1)
        self.time_connection, addr = self.time_tcpSock.accept()
        print "time_tcp connect successful"
        self.time_sub = rospy.Subscriber("/clock", Clock, self.__recv_time)


    def __recv_time(self,data):
        """
        Get the time of the platform
        :param data:
        :return:
        """
        buff = cStringIO.StringIO()
        data.serialize(buff)
        try:
            if(self.time_connection!=None):
                self.time_connection.send(buff.getvalue())
        except Exception,msg:
            print msg
            self.time_connection.close()
            self.time_connection=None
            self.time_sub.unregister()

    def __del__(self):
        if self.time_connection!=None:
            self.time_connection.close()
        self.time_tcpSock.close()

    def __shutdown(self):
        self.time_sub.unregister()
        if self.time_connection!=None:
            self.time_connection.close()
        self.time_tcpSock.close()



if __name__ == '__main__':
    my_time=GazeboTime()
    rospy.spin()
