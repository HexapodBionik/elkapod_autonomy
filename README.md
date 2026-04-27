## Setting up the camera in the simulation:

`cd /elkapod_sim_ws/src/camera_ws` 

`rosdep install --from-paths src/oak_camera --ignore-src -y`

`cd /elkapod_sim_ws`

`colcon build --symlink-install --packages-select oak_camera`

`source install/setup.bash`

`sudo apt update && sudo apt install ros-jazzy-depthai-ros-msgs`

## Fast launch/rebuild:

`cd /elkapod_sim_ws`

`rm -rf build/oak_camera install/oak_camera`

`colcon build --symlink-install --packages-select oak_camera`

`source install/setup.bash`

## Launching command


`ros2 launch oak_camera depth_camera.launch.py 
sim:={true | false}`



TODO:
write more detailed docs



