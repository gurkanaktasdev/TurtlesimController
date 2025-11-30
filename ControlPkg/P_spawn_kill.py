#!/usr/bin/env python3 
import random
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Spawn,Kill
from my_first_interfaces.msg import Turtle,Turtles    # Custom interfaces


class TrutleSpawn(Node):

    def __init__(self):
        super().__init__("spawANDkillNode")
        self.declare_parameter("Target_size",5)
        self.target_size = self.get_parameter("Target_size").value
        self.turtles_loc = Turtles()
        self.turtle_x = 0
        self.turtle_y = 0
        
        self.client_spawn = self.create_client(Spawn,"/spawn")
        self.publisher_ = self.create_publisher(Turtles,"alives_turtles",10)  # Güncel turtles ları yayınlar
        self.client_kill = self.create_client(Kill,"/kill")     
        self.sub_turtle1 = self.create_subscription(Pose,"/turtle1/pose",self.checkturtle1,10) # Turtle1(hareketli turtle) ın Pose değişkenlerini alır.
        self.create_timer(1.0,self.spawnCllbc)
        
    def spawnCllbc(self):
        if(len(self.turtles_loc.turtles) < self.target_size):
            while not self.client_spawn.wait_for_service(1.0):
                self.get_logger().info("Waiting /spawn service !!")
            
            data = Spawn.Request()
            data.x = random.uniform(0.01,10.0)
            data.y = random.uniform(0.01,10.0)
            data.theta = random.uniform(-3.0,3.0)
            
            self.turtle_x = data.x
            self.turtle_y = data.y

            future = self.client_spawn.call_async(data)
            future.add_done_callback(self.spawnResponseCll)

        if(len(self.turtles_loc.turtles) != 0):
            self.publisher_.publish(self.turtles_loc)

    

    def spawnResponseCll(self,future):
        try:
            response = future.result()
            turtle_name = response.name
            turtle_sample = Turtle()
            turtle_sample.x = self.turtle_x
            turtle_sample.y = self.turtle_y
            turtle_sample.name = turtle_name
            self.turtles_loc.turtles.append(turtle_sample)
        except:
            self.get_logger().warn("Spawn service has been denied !!")
        

    def checkturtle1(self,data:Pose):  #Turtle1 in pose değeri ile listedeki turtlelardan herhangi biri ile üst üste gelirse onu yok etmemize yarayan fonskiyon
        if len(self.turtles_loc.turtles) != 0:
            for index,turtle in enumerate(self.turtles_loc.turtles):
                if(abs( turtle.x - data.x) < 0.25 and abs( turtle.y- data.y) < 0.25):
                    while not self.client_kill.wait_for_service(1.0):
                        self.get_logger().info("Waiting for /kill service !!")
                    
                    delete = Kill.Request()
                    delete.name = turtle.name

                    self.client_kill.call_async(delete)
                    self.turtles_loc.turtles.pop(index)
            

def main(args=None):
    rclpy.init(args=args)
    node = TrutleSpawn()
    rclpy.spin(node)
    rclpy.shutdown()       

if __name__ == "__main__":
    main()    