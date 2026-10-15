# TM5 Python Control & Camera

Minimal terminal control for a Techman TM5 robot: **select joint 1–6, then enter +degrees or -degrees.**

Joint control uses the Python standard library. Camera capture and live preview use the official EIH Camera gRPC API with the dependencies listed below. **No ROS or PC-side TMflow installation is required.** Joint motion requires a running TMflow Listen project on the robot; camera access uses a separate controller service.

## Installation and quick start (Windows)

Install Python with Tcl/Tk support and Git, or download this repository as a ZIP and extract it. Internet access is needed for the initial package installation; operation uses the local robot network.

The tested environment is Windows with Python **3.9.13**, TM5-900, controller HW **3.2B**, and TMflow **2.26.3800.NA**. Other Python/controller combinations have not been verified here.

```powershell
git clone https://github.com/evan6007/tm5-python-tcp-control.git
cd tm5-python-tcp-control
python setup_camera.py
```

The installer creates `.venv-camera`, installs pinned packages, and checks imports without connecting to the robot. It does not change the base/Conda environment. No environment activation is needed afterward.

| Task | Command | How to exit |
|---|---|---|
| One relative joint movement | `python control.py` | Enter at the joint prompt |
| Save one camera image | `python camera.py` | Exits after saving |
| Continuous camera preview | `python camera_live.py` | Q, Esc, or close the window |

If you only need joint control, skip `setup_camera.py`; no pip dependencies are required for `control.py`.

Camera runtime packages are pinned in `requirements-camera.txt`: `grpcio`, `protobuf`, and `Pillow`. Tkinter comes with the Python installation. Generated protobuf modules are included, so end users do not need a compiler or `grpcio-tools`.

## Camera setup and operation

1. **Stop the running TMflow project before opening settings.** On the tested controller, Services was hidden while the project was running.
2. Open **Configuration → Vision Settings → Services → EIH Camera API**.
3. Set Status to **Enabled**. If an IP filter is configured, allow the laptop's Ethernet IP.
4. Run `python camera_live.py` for continuous preview, or `python camera.py` for a single image.

The camera service uses **gRPC on TCP 15567**. It does not require the Listen project to run. Camera scripts send no joint-motion commands and do not change exposure, focus, resolution, or other camera settings.

Default robot address: `192.168.1.101`. For a snapshot, use `python camera.py --ip YOUR_ROBOT_IP`. For preview, edit `ROBOT_IP` near the top of `camera_live.py`.

Snapshots are saved to `camera_captures/` with timestamped names. Live preview does not save images. Captures and virtual environments are excluded from Git.

### Preview performance

The preview repeatedly requests individual PNG images via `getImageData`; it is not an RTSP/H.264 video stream. The controller returned 1280 × 960 images in this session; the preview displays them at up to 960 × 720. Its title shows measured display FPS.

A 20-frame local measurement on 2026-10-15 recorded approximately **175 ms per API response**, **30 ms for decoding/resizing**, and **4.9 FPS** for sequential acquisition. These are observations, not guaranteed camera specifications. The preview was subsequently adjusted to remove a 30 ms delay and use faster resizing; a new benchmark of that revision has not been recorded. TMvision jobs take priority and can delay API requests.

### Troubleshooting

| Symptom | Action |
|---|---|
| `No module named google.protobuf`, `grpc`, or `PIL` | Run `python setup_camera.py`. Camera entry points automatically use `.venv-camera` when it exists. |
| `No module named tkinter` | Install/repair Python with Tcl/Tk support, then recreate the camera environment if needed. |
| Only External Hard Drive appears under Vision Settings | Stop the running project and reopen Vision Settings. |
| Camera API connection timed out | Check robot IP, Ethernet connection, EIH Camera API status, and IP filter. |
| Camera API reachable but camera disconnected | Check camera status on the controller; the script does not reset or reconnect camera hardware. |
| Frozen preview or a disconnected message | Check the controller and competing vision jobs, close the preview, and restart it. |
| Slow preview | Check the displayed FPS; this API transfers individual PNGs. The recorded baseline was about 5 FPS. |
| Joint control says Listen is inactive | Run `PC_Control` and confirm execution is waiting at Listen1. |

Use one preview instance at a time. Closing a camera window only closes the camera client.

## Run

```sh
git clone https://github.com/evan6007/tm5-python-tcp-control.git
cd tm5-python-tcp-control
python control.py
```

The program displays the current angles, then asks for:

1. **Joint:** `1` to `6` (Enter alone exits).
2. **Change:** a signed number in degrees, such as `+1` or `-0.5`.

Example: `6`, then `+1` means **increase J6 by 1 degree from its live position**. It does not mean move J6 to an absolute angle of 1 degree. The other five joint targets come from live readback.

**Pressing Enter after the change sends one move after automatic state checks. There is no second confirmation, automatic return, or repetition.** Ctrl+C cancels before submission; it does not stop an already issued motion.

## Controller setup

Example direct Ethernet connection:

| Device | IPv4 | Mask |
|---|---|---|
| Laptop | `192.168.1.100` | `255.255.255.0` |
| Robot | `192.168.1.101` | `255.255.255.0` |

Edit `IP` in `control.py` if your robot uses another address.

On the controller:

1. In **Configuration → Communication → Ethernet Slave**, disable the service while editing the data table.
2. Select **Binary** and include `Robot_Link`, `Robot_Error`, and `Joint_Angle`. `Coord_Robot_Flange` may also remain selected. Save and enable the service. Ethernet Slave **Write Permission is not required**.
3. Create a Flow project named `PC_Control`: **Start → Listen1**. Keep the Listen entry message `"Listen1"` and the connection/data timeouts at `0` for this session setup.
4. Run the project and enter `Listen1`. Initial tests used **M mode and 5% project speed**. Follow the robot's normal enabling-device and safety procedures; this software does not change them.

The TMflow project and data table live on the controller; this repository contains instructions, not an exported controller project.

## Speed

Edit this line near the top of `tm_tcp.py`, save, then restart Python:

```python
SPEED_PERCENT = 3
```

This is the PTP command's speed percentage. The Robot Stick project-speed setting also affects motion. Actual speed depends on operating mode, safety limits, acceleration and travel distance. A percentage is not degrees per second.

## Protocol

| TCP port | Protocol | Purpose |
|---|---|---|
| 5891 | TMSVR | Live joint/error state |
| 5890 | TMSTA | Check `Listen1` state |
| 5890 | TMSCT | Send TMscript `PTP("JPP",...)` |
| 15567 | gRPC / protobuf | EIH camera images |

Python converts the requested relative change into absolute joint targets using fresh robot feedback. No Modbus, EtherNet/IP or cloud service is involved.

## Files and offline tests

- `control.py`: short interactive entry point.
- `tm_tcp.py`: TCP framing, checksum validation, binary decoding and one-shot motion.
- `test_offline.py`: simulated connections; never connects to a physical robot.
- `camera.py` / `camera_live.py`: snapshot and continuous preview.
- `camera_env.py` / `setup_camera.py`: environment selection and installation.
- `camera_api/`: official protobuf schemas, generated Python modules, upstream license and provenance.
- `requirements-camera.txt` / `requirements-dev.txt`: runtime and optional code-generation dependencies.
- `README.txt` / `交接說明.txt`: plain-text quick-start notes.

```sh
python -m unittest -v test_offline
```

## Operating limits

One joint per invocation, with **no application-imposed angular step cap**. Robot-controller joint and safety limits still apply. The current command speed setting is 3%, acceleration time 1000 ms, blending 0.

The code rejects non-finite numbers, robot errors, inactive Listen state, and motion/pose changes during preflight. It never automatically retries a motion. Arrival is checked using three consecutive readings within 0.03 degrees per joint, with a 300-second observation timeout.

These checks are **not collision protection or a certified safety system**. A larger step can sweep a large area. The on-site operator must check mounting, clearance, tools/loads and operating mode. The verified initial setup had no gripper.

**Closing Python, Ctrl+C, or disconnecting Ethernet does not stop issued motion.** Use Robot Stick STOP for normal stopping and E-stop in an emergency. After a timeout/error, stop the project and inspect before retrying.

## Verification record

- Session hardware: TM5-900, controller HW 3.2B, TMflow 2.26.3800.NA.
- Physically verified earlier in the session: state readback, Listen query, arithmetic TMscript, and one J6 +1-degree motion.
- This packaged relative-control revision passed offline tests. It has **not** undergone additional physical-motion validation or general safety acceptance.
- Camera snapshot saved and visually inspected at 1280 × 960; preview received at least 30 consecutive frames. The base-Python environment launcher was tested with a successful snapshot.

## 中文快速說明

第一次安裝：在專案資料夾執行 `python setup_camera.py`。之後不需要切換 Conda 或啟動虛擬環境。

- 即時相機：`python camera_live.py`，按 Q／Esc 或關閉視窗結束。
- 拍一張：`python camera.py`，照片存在 `camera_captures`。
- 相機設定：先停止 TMflow 專案，再到 Vision Settings → Services → EIH Camera API 啟用。
- 手臂和相機分別走 TCP 指令與 gRPC，全部不需要 ROS。

執行 `python control.py` → 顯示現在角度 → 輸入 `1～6` 選軸 → 輸入 `+數字` 或 `-數字` 表示從目前角度加減幾度。

**增量輸入後按 Enter 就送出，不再輸入 MOVE。**速度在 `tm_tcp.py` 的 `SPEED_PERCENT` 調整。結束 Python 不等於停機，停止請用操作棒。

## Official references

- [Techman Listen and Ethernet Slave setup](https://github.com/TechmanRobotInc/tm2_ros2/blob/humble/doc/tm_humble.md)
- [Techman developer area](https://www.tm-robot.com/en/support/developer-area)
- [Official EIH Camera API client and protocol schemas](https://github.com/TechmanRobotInc/tm_eih_cam_client)

## Protocol maintenance and attribution

The official schemas and upstream license are retained in `camera_api/`; `SOURCE.txt` records the upstream commit. To regenerate the included Python modules:

```powershell
.venv-camera\Scripts\python -m pip install -r requirements-dev.txt
.venv-camera\Scripts\python -m grpc_tools.protoc -I camera_api --python_out=camera_api camera_api/EIHCamera.proto camera_api/EIHCameraAPI.proto
```

Do not edit generated `*_pb2.py` files manually. Laboratory photos, local environments, and the machine-specific launcher are not distributed.

This is an independent handoff example, not an official Techman product.
