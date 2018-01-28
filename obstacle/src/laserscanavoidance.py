#! /usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

rospy.init_node('robot_cleaner')

pub = rospy.Publisher('/cmd_vel_mux/input/teleop', Twist, queue_size=10)
rate = rospy.Rate(2) # refresh rate of messages
count = Twist() # message that takes the linear and angular velocties of the robot

# After each message published, this function is called to determine
# whether to stop and turn, or keep going linearly, and then to publish its
# current state to the cmd_vel topic
def callback(msg):
    start()
    turn(msg)
    vel_pub(count)  # Publish messages to the topic teleop is subscribed to

# If distance to obstacle is too close, stop and turn.
def turn(msg):
    # Find angle of obstacle that is too close
    minDistance = 31 # max laser range is 30
    obsDirection = 0 # angle of obstacle from robot
    
    # range of robot laser 180:540 to include a large span but not the extreme
    # edges - 360 is directly in front of the robot
    
    for angle, distance in enumerate(msg.ranges[180:540]):
        if distance < minDistance:
            minDistance = distance
            obsDirection = angle

    if (minDistance < 0.5):
        # Too close: stop.
        count.linear.x = 0
        if (obsDirection < 180):
            # Turn right
            count.angular.z = 3
        else:
            # Turn left
            count.angular.z = -3

# On start, go straight with no angular velocity
def start():
    count.linear.x = 0.5
    count.angular.z = 0

# Message publisher function - publishes to /cmd_vel
def vel_pub(msg):
    pub.publish(msg)

# Continually loop while robot is launched
while not rospy.is_shutdown():
    pub.publish(count) # publish current robot velocities
    sub = rospy.Subscriber('/scan', LaserScan, callback) # ensure the laser scan subscribes to the topic callback
    rate.sleep() # allow execution of instructions
