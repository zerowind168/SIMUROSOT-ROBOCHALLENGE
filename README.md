# SIMUROSOT ROBO CHANLLENGE 
=============
<br>
This is the 2019 FIRA SIMUROSOT ROBO CHANLLENGE environment<br>

OS: ubuntu 16.04<br>
ROS: Kinectic<br>

##### :exclamation:You must not install the ROS on a(any) Virtual Machine, otherwise there will be a lot of problems.:exclamation:
## 1. Notice:
This competition mainly uses vision to avoid obstacles.In the game, you need to adjust the position information of the car through vision.
Summary:
You can only get images from the platform server, and then send commands to the server to control the car.
## 2. Install the ROS:<br>
You can go to:  http://wiki.ros.org/kinetic/Installation/Ubuntu
for how to download the ROS Kinetic version.<br>
Here we copy some of the proceed below:<br>

1. Setup your sources.list

    ```
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    ```
2. Setup your keys
    ```
    sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
    ```
3. Installation
    ```
    sudo apt-get update
    sudo apt-get install ros-kinetic-desktop-full
    ```
4. Initialize rosdep
    ```
    sudo rosdep init
    rosdep update
    ```
5. Environment setup
    ```
    echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    ```

## 3. Turtlebot & Gazebo Package

    ```
       sudo apt-get install ros-kinetic-turtlebot-gazebo
    ```
   
## 4. SIMUROSOT-ROBOCHALLENGE
### 4.1 Download this project
### 4.2 Add the modles
In your home directory, Press Ctrl+H to show the hidden directory, then go to gazebo/models sub-directory. Copy the models1/newbox and models1/newfield models1/colorbox to this directory.

### 4.3 Run the program <br>
There are two modes of running programs. The first is to run both the server and the client on one machine, and the second is to run the server and client on two machines.The following will explain how to run these two modes:
#### 4.3.1 Run both the server and the client on one machine:
##### 4.3.1.1 Open a terminal and transfer to the current path(~/ros_scripts/)
##### 4.3.1.2 When you run the robot_ser.py file, enter a file name to record the game information.
   ```
   export LD_LIBRARY_PATH=~/ros_scripts/plugin:$LD_LIBRARY_PATH
   roslaunch turtlebot_gazebo turtlebot_world.launch world_file:=/home/username/ros_scripts/world/world1-1
   ```
if you have trouble run the roslaunch, try to run the following first : 
   ```
roslaunch turtlebot_gazebo turtlebot_world.launch
   ```
   here username should be replaced with your username. And you can run another world_file just by replace the world1-1 to another one.
   open a terminal and run : 
   ```
   python robot_ser.py
   ```
   you will see a prompt >>, you can input a string which is a file name , and the log will be saved to this file.
   then you can open another terminal and run:
   ```
   python how_to_run.py 
   ```

#### 4.3.2 Run the server and client on two machines:
##### 4.3.2.1 Suppose you choose A computer as the server and B computer as the client.
##### 4.3.2.2 Download this project on both computer.On the client side, change the ip in the robot_cli.py and clock_cli.py files to the IP address of the A computer.
##### 4.3.2.3 On the Server 
   ```
   export LD_LIBRARY_PATH=~/ros_scripts/plugin:$LD_LIBRARY_PATH
   roslaunch turtlebot_gazebo turtlebot_world.launch world_file:=/home/username/ros_scripts/world/world1-1
   ```
   here username should be replaced with your username. And you can run another world_file just by replace the world1-1 to another one.
   ```
   python clock_ser.py
   python robot_ser.py
   ```
##### 4.3.2.4 On the client
   ```
   roscore
   python clock_cli.py
   python how_to_run.py
   ```
  
If you see the figure as follow, you are success.
![image](https://github.com/zerowind168/SIMUROSOT-ROBOCHALLENGE/blob/master/roboc.png) 
## 5. File Explain 
### 5.1 The file structure 

./ros_scripts<br>
├── how_to_run.py<br>
├── robot.py<br>
├── robot_ser.py<br>
├── robot_cli.py<br>
├── clock_ser.py<br>
├── clock_cli.py<br>
├── judge.py<br>
└── world.world<br>

## 5.2 detail explain for the file
#### 1. how_to_run.py
This script define how the turtlebot act. There is only one function "Run" in this script, The function has a "robot" parameter, which is an object of class "Robot".
#### 2. robot.py
This script define a Robot class.Mainly describes the function of the robot.<br>
set_move_speed(met_per_sec)　: Set the speed of turtlebot，dimension is m/s.<br>
set_turn_speed(deg_per_sec)　: Set the rotate speed of turtlebot, dimension is degree/s.<br>
go_forward(seconds)　　　　 : Let the turtlebot move for "seconds" seconds at the given speed.<br>
turn_around(seconds)　　　　: Let the turtlebot turn around for "seconds" seconds at the given rotate speed.<br>
get_image()　　　　　　　　: Get the current image from camera. The image contain the RGB information as a 2D matrix.
#### 3. robot_ser.py
The script mainly defines how to receive information from the robot and calls the function to control the robot.
#### 4. robot_cli.py
The script mainly defines how to receive the state information of the robot from the server and send control commands to the server.
#### 5. clock_ser.py
Record the time of the server to synchronize with the client
#### 6. clock_cli.py
Record the time of the client to synchronize with the server
#### 7. judge.py
This script is used to record the robot's game time and determine whether the game is successfully completed.
#### 4. world.world
This file define the enviroment which include play field and obstacles. It will be called by "start.py" script. We have defined some more testing enviroment in the "world" sub-directory. You can use them for testing. 

## 5.3 More to do
The given demo is really simple for beginners to start up. You can define more sophisticate function based on "robot.move_cmd" and "robot.turn_cmd" to set. And using "robot.cmd_vel.publish(robot.move_cmd)" to publish you manipulation. Such as simulatanious turn around and moving.

# 6. This game will have two challenges of different difficulty.
![image](https://github.com/zerowind168/SIMUROSOT-ROBOCHALLENGE/blob/master/challenge1.png) 
![image](https://github.com/zerowind168/SIMUROSOT-ROBOCHALLENGE/blob/master/challenge2.png) 
## 6.1 How to change scene information
You only go to the path .gazebo/models/newbox/materials/textures,then exchange the naming of two images

# 7. Future Work
The compatible is not good. The platform can only run on gazebo7.0.0, and if you update the gazebo, some problem will occur. 
So for the future, the enviroment should run on a more varity platform. For different OS, ROS and GAZEBO version.


 






