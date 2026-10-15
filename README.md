# TM5 Python TCP Control

Minimal terminal control for a Techman TM5 robot: **select joint 1–6, then enter +degrees or -degrees.**

Python standard library only. **No ROS, no pip packages, no PC-side TMflow required.** The robot controller must run its TMflow Listen project.

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

Python converts the requested relative change into absolute joint targets using fresh robot feedback. No Modbus, EtherNet/IP or cloud service is involved.

## Files and offline tests

- `control.py`: short interactive entry point.
- `tm_tcp.py`: TCP framing, checksum validation, binary decoding and one-shot motion.
- `test_offline.py`: simulated connections; never connects to a physical robot.
- `README.txt` / `交接說明.txt`: plain-text handoff notes. The laptop-specific `ready.cmd` mentioned there is not distributed; use `python control.py`.

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

## 中文快速說明

執行 `python control.py` → 顯示現在角度 → 輸入 `1～6` 選軸 → 輸入 `+數字` 或 `-數字` 表示從目前角度加減幾度。

**增量輸入後按 Enter 就送出，不再輸入 MOVE。**速度在 `tm_tcp.py` 的 `SPEED_PERCENT` 調整。結束 Python 不等於停機，停止請用操作棒。

## Official references

- [Techman Listen and Ethernet Slave setup](https://github.com/TechmanRobotInc/tm2_ros2/blob/humble/doc/tm_humble.md)
- [Techman developer area](https://www.tm-robot.com/en/support/developer-area)

This is an independent handoff example, not an official Techman product.
