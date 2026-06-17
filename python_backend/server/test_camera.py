import sys
import os
import time

# Add python_backend path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.camera_manager import start_camera, stop_camera, get_camera_status

print("Starting CCTV camera server...")

message = start_camera("CAM_1", 0)
print(message)

try:
    while True:
        print(get_camera_status())
        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping camera...")
    stop_camera("CAM_1")