#!/usr/bin/env python3

import rclpy,math
from rclpy.node import Node
from my_first_interfaces.msg import Turtles,Turtle  # Custom Interfaces
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty


class ControlTurtle(Node):

    def __init__(self):
        super().__init__("controlTurtle_nodes")
        self.kp_dist = 1.0
        self.kp_angle = 1.6
        self.main_turtle = Pose()
        self.sub_trts = self.create_subscription(Turtles,"alives_turtles",self.ctrlTurtleClbk,10)
        self._sub_trtPose = self.create_subscription(Pose,"/turtle1/pose",self.poseClbk,10)
        self.publisher_cmd = self.create_publisher(Twist,"/turtle1/cmd_vel",10)
        self.clear_srv = self.create_client(Empty,"/clear")
        self.clear_timer = self.create_timer(20,self.clearClbk)    

    def clearClbk(self):        # Belirli periyotlar ile ekran tmeizliği için
        while not self.clear_srv.wait_for_service(1.0):
            self.get_logger().info("Waiting /clear service !!")
        
        req = Empty.Request()
        self.clear_srv.call_async(req)

    def poseClbk(self,msg:Pose):     # Main turtle'ın anlık pose değerini almak için 
        self.main_turtle = msg

    def ctrlTurtleClbk(self,msg:Turtles):   #Ana kontrol fonksiyonu
        if len(msg.turtles) == 0:
            return

        index,dist = self.checkCLosetTurtles(msg)
        if index == -1:
            return
        
        target = msg.turtles[index]
        self.rotateTarget(target,dist)


    def checkCLosetTurtles(self,turtleList:Turtles):     # Gelen listeden en yakın turtle ın konumunu dönen func.
        if len(turtleList.turtles) == 0:
            return -1, float("inf")
        
        min_dist = 100
        min_index = 0
        for index,turtle in enumerate(turtleList.turtles):
            distance_x = abs(self.main_turtle.x - turtle.x)
            distance_y = abs(self.main_turtle.y - turtle.y)
            dist_hip = math.sqrt(distance_x*distance_x + distance_y*distance_y)
            if dist_hip < min_dist:
                min_dist = dist_hip
                min_index = index
        
        return min_index,min_dist

    def rotateTarget(self,target:Turtle,dist):     # Aksiyon alınan func.

        expected_theta = math.atan2(target.y - self.main_turtle.y,target.x - self.main_turtle.x) # Hedefe gerkli olan açı
        
        msg = Twist()
        msg.linear.x = min(dist* self.kp_dist,4.0)
        if msg.linear.x < 0.5:
            msg.linear.x = 0.5

        fark = expected_theta - self.main_turtle.theta
        while fark > math.pi:
            fark -= 2*math.pi
        while fark < -math.pi:
            fark += 2*math.pi

        msg.angular.z = fark * self.kp_angle

        if msg.angular.z > 4.0:
            msg.angular.z = 4.0
        if msg.angular.z < -4.0:
            msg.angular.z = -4.0

        self.publisher_cmd.publish(msg)

def main(args = None):
    rclpy.init(args=args)
    node = ControlTurtle()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()