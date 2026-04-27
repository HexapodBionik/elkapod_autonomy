from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    ExecuteProcess,
    LogInfo,
    RegisterEventHandler,
    TimerAction
)
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.event_handlers import (
    OnExecutionComplete,
    OnProcessExit,
    OnProcessIO,
    OnProcessStart,
    OnShutdown
)
from launch.events import Shutdown
from launch.substitutions import (
    EnvironmentVariable,
    FindExecutable,
    LaunchConfiguration,
    LocalSubstitution,
    PythonExpression
)

def generate_launch_description():
   sim_mode = LaunchConfiguration('sim')

   sim_arg = DeclareLaunchArgument(
      'sim',
      default_value='false',
      description = 'Use Gazebo simulation'
    )
   return LaunchDescription([
      sim_arg,
      
      Node(
            package='oak_camera',

            executable='obstacle_node',
            parameters=[{'sim': LaunchConfiguration('sim')}] # Passes the launch arg to the node

   
      ),
    
      Node(
            package='depthai_ros_driver_v3',
            executable='driver_node',
            name='oak',  # This ensures topics start with /oak/...
            condition=UnlessCondition(sim_mode),
            output='screen'
)
   ])

