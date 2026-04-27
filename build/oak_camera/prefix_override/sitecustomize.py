import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/elkapod_sim_ws/src/camera_ws/install/oak_camera'
