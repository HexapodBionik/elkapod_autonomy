

import rclpy
from rclpy.node import Node
from depthai_ros_msgs_v3.msg import SpatialDetectionArray
from geometry_msgs.msg import Twist
from vision_msgs.msg import Detection3DArray
from sensor_msgs.msg import PointCloud2 
import numpy as np
import sensor_msgs_py.point_cloud2 as pc2

class SafetyControlNode(Node):
    def __init__(self):
        super().__init__('obstacle_detection_node')
        
        #Parameter for the simulation. 
        self.declare_parameter('sim', False)
        
        use_sim = self.get_parameter('sim').get_parameter_value().bool_value

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('Obstacle detection node is ONLINE.')

        if use_sim:
        
            self.sim_subscription = self.create_subscription(PointCloud2, '/front_camera/points', self.point_callback, 10)
        
        else:
            self.real_subscription = self.create_subscription(Detection3DArray, '/oak/nn/spatial_detections', self.detection_callback, 10)
            
 
    
    #Function for simulated camera.
    #It takes PointCloud2 object.
    def point_callback(self, msg: PointCloud2):
        self.get_logger().info('Obstacle detection node is working with PointCloud2', once = True)
        points = pc2.read_points_numpy(msg, field_names=("x", "y", "z"), skip_nans=True)
       
        #DEBUG
        sample = points[len(points)//2] # Get a point from the middle of the list
        self.get_logger().debug(f"Sample Point middle: X={sample[0]:.2f}, Y={sample[1]:.2f}, Z={sample[2]:.2f}")


        if points.size == 0:
            return

       #Those masks define a box.
       # if a point apears here it goes into obstacle_points_warn list
       # The warning box is : (0.5 ; 1) meters away; 0.6[0.3*2] meters wide; and 0.05 m from the floor
        mask_warn = (points[:, 0] > 0.5) & (points[:, 0] < 1.0) & \
            (np.abs(points[:, 1]) < 0.3) & \
            (points[:, 2] > 0.05) 

        # if a point apears here it goes into obstacle_points_stop list
        #The stop box is : (0.1 ; 0.5] meters away; 0.6[0.3*2] meters wide; and 0.05 m from the floor
        #<= 0.5 to prevent printing warn and error at one time
        mask_stop = (points[:, 0] > 0.1) & (points[:, 0] <= 0.5) & \
            (np.abs(points[:, 1]) < 0.3) & \
            (points[:, 2] > 0.05)

        obstacle_points_warn = points[mask_warn]
        obstacle_points_stop = points[mask_stop]
        



        if len(obstacle_points_warn) > 20: # If we see more than 20 dots in the warn box
            distances = obstacle_points_warn[:, 0]
            closest_point = np.min(distances)
            self.get_logger().warn(f"WARNING: Object detected at {closest_point} m")
            


        elif len(obstacle_points_stop)>20:# If we see more than 20 dots in the stop sbox
            distances = obstacle_points_stop[:, 0]
            closest_point = np.min(distances)
            self.get_logger().error(f"STOP! Object at {closest_point}m")
            self.send_stop_command()
            

    #Function for real oak camera.
    #It takes Detection3DArray object, which is already prosessed by depthai_ros_driver_v3
    def detection_callback(self, msg: Detection3DArray): 
        self.get_logger().info('Obstacle detection node is working with Detection3DArray', once = True)

       
        for detection in msg.detections:
            
            dist = detection.results[0].pose.pose.position.z
            self.get_logger().info(str(dist))
            
            if dist < 0.5: # 50 cm
                self.get_logger().error(f"STOP! Object at {dist}m")
                self.send_stop_command()
            elif dist < 1.0: # 1 meter
                self.get_logger().warn(f"WARNING: Object detected at {dist}m")
                print(f"Safety Alert: Object is {dist*100:.1f} cm away")

    #Function for stoppinf the robot
    def send_stop_command(self):
        msg = Twist()
        # All values (linear.x, angular.z) are 0.0 by default
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SafetyControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()



