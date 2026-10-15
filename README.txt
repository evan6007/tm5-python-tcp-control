TM5 PYTHON CONTROL & CAMERA
==========================
Repository: https://github.com/evan6007/tm5-python-tcp-control
Full installation, controller setup, limitations and troubleshooting: README.md

INSTALL (Windows)
1. Install Python with Tcl/Tk support. Verified: Python 3.9.13.
2. Clone or download this repository.
3. Open a terminal in this folder and run:
   python setup_camera.py
The installer uses a local .venv-camera; it does not change your base environment.
Joint control alone needs no pip packages. No ROS is required.

RUN
python control.py       Select joint 1-6, then enter +/- degrees.
python camera.py        Save one image to camera_captures/.
python camera_live.py   Continuous preview. Q / Esc / close window to exit.

ROBOT SETUP
Default robot IP: 192.168.1.101. Example laptop IP: 192.168.1.100/24.
Motion: configure Ethernet Slave binary feedback and run Start -> Listen1.
Camera: stop the project, then Configuration > Vision Settings > Services >
EIH Camera API > Enabled. Camera uses gRPC port 15567, independently of Listen.
See README.md for the exact feedback fields and IP settings.

MOTION
A signed value changes the selected joint relative to LIVE readback.
Pressing Enter after the value sends one move; there is no second confirmation.
Speed: SPEED_PERCENT in tm_tcp.py (current default 3).
There is no application angular-step cap. Controller safety limits still apply.
Closing Python or disconnecting the network does NOT stop issued motion.
Use Robot Stick STOP for normal stopping; E-stop in an emergency.

CAMERA
Preview repeatedly retrieves PNG images; it is not an RTSP video stream.
Measured sequential acquisition was about 4.9 FPS in this setup.
Snapshots stay local; preview does not save photos or move the robot.
If imports fail, rerun python setup_camera.py.

中文快速入門
第一次：python setup_camera.py
即時影像：python camera_live.py，Q / Esc 關閉。
拍照：python camera.py，存到 camera_captures。
控制：python control.py，輸入軸 1~6，再輸入 +/- 角度，Enter 就送出。
速度在 tm_tcp.py 的 SPEED_PERCENT。結束 Python 不等於停止手臂。
完整英文說明、故障排除與實測紀錄請看 README.md。
