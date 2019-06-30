# coding=utf-8
import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Point
from rosgraph_msgs.msg import Clock
from socket import*
import os
import threading
from robot import Robot
import how_to_run
import time
class judge:
    def __init__(self,filename):
        rospy.init_node('turtlebot_robot', anonymous=False)
        rospy.loginfo("Press ctrl+c to stop!")
        rospy.on_shutdown(self.__shutdown)
        self.filename=filename
        self.robot_pos_now=Point()
        self.robot_pos_now.x=self.robot_pos_now.y=0
        self.robot_pos_last=self.robot_pos_now
        self.time_begin=None
        self.time_now=None
        self.time_sub=rospy.Subscriber("/clock",Clock,self.__recv_time)
        self.state_sub = rospy.Subscriber("/gazebo/model_states", ModelStates, self.__recv_states)
        self.isEnd=False
        self.lastCollision=""
        self.t=threading.Thread(target=self.contact)
        self.t.setDaemon(True)
        self.t.start()

    def __recv_time(self,data):

        if self.time_begin==None:
            self.time_begin=data.clock.to_time()
        self.time_now=data.clock.to_time()
        if(self.time_now-self.time_begin>=180)and not self.isEnd:
            self.isEnd=True
            self.writeData("time out")

    def __recv_states(self,model_states):

        name = 'mobile_base'
        for i in xrange(len(model_states.name)):
            if name==model_states.name[i]:
                pos=model_states.pose[i].position
        self.robot_pos_last=self.robot_pos_now
        self.robot_pos_now=pos
        if self.successful(self.robot_pos_now) and not self.isEnd:
            self.isEnd=True
            self.writeData("successful:time="+str(self.time_now-self.time_begin))
        if (not self.isEnd) and self.inside(self.robot_pos_last) and (not self.inside(self.robot_pos_now)):
            self.writeData("outside:"+str(self.time_now))

    def writeData(self,message):
        with open(self.filename,'a') as file:
            file.write(message+'\n')
        print message

    def inside(self,postion):

        if postion.x<=6 and postion.x>=-0.05 and postion.y<=1.5 and postion.y>=-1.5:
            return True
        else:
            return False

    def successful(self,postion):

        if postion.x>5.95 and postion.x<6.05 and postion.y>-0.7 and postion.y<0.7:
            return True
        else:
            return False

    def contact(self):

        udpSerSock = socket(AF_UNIX, SOCK_DGRAM)
        if os.path.exists("/tmp/contacts"):
            os.unlink("/tmp/contacts")
        udpSerSock.bind("/tmp/contacts")
        udpSerSock.settimeout(1)
        while not self.isEnd:
            try:
                data, addr = udpSerSock.recvfrom(1024)
                if (data is not None) and (data!="") and (data!=self.lastCollision):
                    self.lastCollision=data
                    self.writeData(data+":"+str(self.time_now))
            except Exception:
                pass

    def __shutdown(self):
        if not self.isEnd:
            self.writeData("stop:time="+str(self.time_now-self.time_begin))
            self.isEnd=True
        self.state_sub.unregister()
        self.state_sub.unregister()

    def __del__(self):
        self.isEnd=True

if __name__=='__main__':
    filename = raw_input(">>")
    my_judge=judge(filename)
    robot = Robot()
    how_to_run.Run(robot)
