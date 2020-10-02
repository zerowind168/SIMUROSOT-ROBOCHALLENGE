# coding=utf-8
import os
from socket import*
import re
import rospy
from geometry_msgs.msg import Twist, genpy
from gazebo_msgs.msg import ModelStates
from sensor_msgs.msg import CompressedImage,Image
from rosgraph_msgs.msg import Clock
import cStringIO
from geometry_msgs.msg import Point
import threading
import struct

class SimServer:
    def __init__(self,filename,world_type=1):
      
        rospy.init_node('turtlebot_robot', anonymous=False)

       
        self.__cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)



       
        self.isEnd = False

        # judge
        self.filename = filename
        self.world_type=world_type
        self.writeData(filename)
        self.robot_pos_now = Point()
        self.robot_pos_now.x = self.robot_pos_now.y = 0
        self.robot_pos_last = self.robot_pos_now
        self.time_begin = None
        self.time_now = None
        # Twist
        self.twist = Twist()

        # tcp config
        self.tcpSock = socket(AF_INET, SOCK_STREAM)
        self.connection = None

        # 
        self.comImage_sub = rospy.Subscriber("/camera/rgb/image_raw/compressed", CompressedImage, self.__recv_comImage)
        self.comImage_data = None

        
        self.image_sub=rospy.Subscriber("/camera/rgb/image_raw",Image,self.__recv_image)
        self.image_data=None
        
        self.state_sub = rospy.Subscriber("/gazebo/model_states", ModelStates, self.__recv_states)
        self.box_pos = None
        
        self.time_sub = rospy.Subscriber("/clock", Clock, self.__recv_time)
        self.time=None
        #contacts
        self.lastCollision = ""
        self.t = threading.Thread(target=self.contact)
        self.t.setDaemon(True)
        self.t.start()


        rospy.on_shutdown(self.__shutdown)



    def serve(self,port=7777):

        self.tcpSock.bind(("", port))
        self.tcpSock.listen(1)
        self.connection, addr = self.tcpSock.accept()
        print "connect successful"
        while not self.isEnd:
            data=""
            try:
                type = self.connection.recv(3)
                if(type=="tws"):
                    data=self.connection.recv(48)
                rospy.loginfo(type+"  "+data)
            except Exception,msg:
                print msg
                continue
            if self.time_begin == None:
                self.time_begin = self.time_now
            if type == "tws":
                self.publish_twist_to_robot(data)
            elif type == "img":
                self.send_img_to_client()
            elif type=="cim":
                self.send_comImg_to_client()
            elif type == "box" and self.world_type!=3:
                self.send_box_pos_to_client()
            elif type == "tim":
                self.send_time_to_client()
            elif type=="end":
                self.isEnd=True
                self.connection.close()



    def publish_twist_to_robot(self, data):
        """
        
        :param data:
        :return:
        """
        try:
            self.twist.deserialize(data)
            self.__cmd_vel.publish(self.twist)
        except genpy.DeserializationError:
            print rospy.loginfo("deserialize twist failed!")

    def send_comImg_to_client(self):
        """
        
        :param image:
        :return:
        """
        buff = cStringIO.StringIO()
        self.comImage_data.serialize(buff)
        flag=struct.pack('i',len(buff.getvalue()))
        self.connection.send(flag)
        self.connection.sendall(buff.getvalue())

    def send_img_to_client(self):
        """
     
        :return:
        """
        buff = cStringIO.StringIO()
        self.image_data.serialize(buff)
        print len(buff.getvalue())
        self.connection.sendall(buff.getvalue())

    def send_box_pos_to_client(self):
         """
        
         :param box_pos:
         :return:
         """
         buff = cStringIO.StringIO()
         self.box_pos.serialize(buff)
         flag=struct.pack('i',len(buff.getvalue()))
         self.connection.send(flag)
         self.connection.sendall(buff.getvalue())

    def send_time_to_client(self):
        """
      
        :return:
        """
        buff = cStringIO.StringIO()
        self.time.serialize(buff)
        self.connection.send(buff.getvalue())


    def __recv_image(self, data):
        """
        
        :param data:
        """
        self.image_data = data

    def __recv_comImage(self,data):
        """
       
        :param data:
        :return:
        """
        self.comImage_data=data

    def __recv_states(self, model_states):
        """
    
        :param model_states:
        :return:
        """
        reg = 'newbox*'
        name = 'mobile_base'
        nameRe = re.compile(reg)
        res = ModelStates()
        for i in xrange(len(model_states.name)):
            if nameRe.match(model_states.name[i]):
                if len(model_states.name)==8 and model_states.name[i]=="newbox_1":
                    continue
                res.name.append(model_states.name[i])
                res.pose.append(model_states.pose[i])
                res.twist.append(model_states.twist[i])
            elif name==model_states.name[i]:
                pos = model_states.pose[i].position
                self.robot_pos_last = self.robot_pos_now
                self.robot_pos_now = pos
                if self.successful(self.robot_pos_now) and not self.isEnd:
                    self.isEnd = True
                    self.writeData("successful:time=" + str(self.time_now - self.time_begin))
                if (not self.isEnd) and self.inside(self.robot_pos_last) and (not self.inside(self.robot_pos_now)):
                    self.writeData("outside:" + str(self.time_now))
        self.box_pos = res

    def __recv_time(self,data):
        """
       
        :param data:
        :return:
        """
        self.time=data
        #juger
        self.time_now=data.clock.to_time()
        if self.time_begin!=None and (self.time_now-self.time_begin>=180)and not self.isEnd:
            self.isEnd=True
            self.connection.close()
            self.writeData("time out")

    def __shutdown(self):
        self.isEnd=True
        if self.connection!=None:
            self.connection.close()
        self.tcpSock.close()
        self.image_sub.unregister()
        self.state_sub.unregister()
        self.time_sub.unregister()
        self.comImage_sub.unregister()

    def __del__(self):
        self.isEnd=True
        if self.connection!=None:
            self.connection.close()
        self.tcpSock.close()


   #####################################################################################
    def writeData(self,message):
        """
        
        :param message:
        :return:
        """
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
        udpSerSock.close()
###########################################################################################裁判

if __name__ == '__main__':
    filename=raw_input(">>")
    server = SimServer(filename)
    server.serve()
