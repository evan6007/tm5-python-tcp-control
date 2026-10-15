TM EIH Camera - single image capture (no ROS)

After setup, either Python environment can launch these commands:
  python camera.py
  python camera_live.py
The scripts automatically use .venv-camera when it exists.

Live preview (continuous images; Q / Esc or close window to exit):
  .venv-camera\Scripts\python camera_live.py
Change ROBOT_IP in camera_live.py if needed. No images are saved by live preview.
中文：camera_live.py 持續顯示即時影像，按 Q、Esc 或關閉視窗結束。

Setup (Windows, from this project folder):
  python -m venv .venv-camera
  .venv-camera\Scripts\python -m pip install grpcio grpcio-tools pillow
  .venv-camera\Scripts\python -m grpc_tools.protoc -I camera_api --python_out=camera_api camera_api/EIHCamera.proto camera_api/EIHCameraAPI.proto

Run:
  .venv-camera\Scripts\python camera.py

Optional robot IP:
  .venv-camera\Scripts\python camera.py --ip 192.168.1.101

Enable in TMflow: Configuration > Vision Settings > Service > EIH Camera.
The official API uses gRPC on port 15567. Allow the laptop IP if an IP filter is configured.
TMvision jobs take priority over API image requests; a busy camera may time out.
Images are saved locally to camera_captures/ (excluded from Git).
This script only checks camera connection and requests an image. It sends no motion or camera-setting commands.

Official protocol files and license: camera_api/
Source: https://github.com/TechmanRobotInc/tm_eih_cam_client

中文：執行 camera.py 拍一張，照片存在 camera_captures。使用獨立相機 API，不使用 ROS，也不會移動手臂。
