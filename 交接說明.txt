TECHMAN TM5 - LIVE RELATIVE JOINT CONTROL

Run: python control.py
No ROS, no pip packages. Python standard library and TCP sockets only.

OPERATION
1. The program reads and displays LIVE J1-J6 angles in degrees.
2. Select ONE joint: 1 through 6. Enter alone exits.
3. Enter a RELATIVE change in degrees. Pressing Enter SENDS the move after state checks.
4. The program reads the angles again and displays current -> target automatically.
5. No MOVE confirmation. Use Ctrl+C BEFORE submitting the delta to cancel.

Example: select 6, enter +1. This means J6 current angle PLUS 1 degree.
You do not enter six absolute angles. Other joints use live readback values.
There is no automatic return or repeated movement.
If the robot moves during preflight, the program refuses the command.
Positive rotation is about the joint axis, not necessarily clockwise as viewed.

CONTROLLER SETUP
Robot: 192.168.1.101. Laptop Ethernet: 192.168.1.100 / 255.255.255.0.
Enable Ethernet Slave, Binary table: Robot_Link, Robot_Error, Joint_Angle.
Coord_Robot_Flange can remain selected. Write Permission is not required.
Run PC_Control: Start -> Listen1. Keep M mode and 5% project speed.
PC-side TMflow is unnecessary; controller-side TMflow must run Listen1.

FILES
control.py: short interactive entry point.
tm_tcp.py: TCP framing, state parsing, one-shot relative joint control.
test_offline.py: run python -m unittest -v test_offline (no robot connection).
ready.cmd: this laptop only; Enter starts the Anaconda Python executable.
On another computer, use python control.py instead of ready.cmd.

PROTOCOL
5891 / TMSVR: live state readback.
5890 / TMSTA: Listen state query.
5890 / TMSCT: TMscript PTP joint-angle motion.
Relative changes are converted internally to absolute joint targets.
No ROS, Modbus, EtherNet/IP or cloud service is used.

LIMITS
One joint at a time. No custom step-size cap; controller joint/safety limits still apply.
PTP command speed 3%, acceleration time 1000 ms, blending 0.
No automatic retry. Arrival requires 3 readings within 0.03 degree per joint, with a 300-second observation timeout.
These checks are NOT collision protection or a certified safety system.
Mounting, clearance, tools/loads and M/A mode must be checked on site.
Other joints sweep more space than J6. The current setup has no gripper.
Closing Python, Ctrl+C or Ethernet disconnection does NOT stop issued motion.
Use Robot Stick STOP to stop normally; use E-stop in an emergency.
On timeout/error, stop the project and inspect before any retry.

VERIFICATION
TM5-900 / controller HW 3.2B / TMflow 2.26.3800.NA.
Earlier session: physical readback, Listen query, arithmetic and J6 +1 verified.
This relative-control revision was tested OFFLINE, with no new physical motion.

REFERENCES
https://github.com/TechmanRobotInc/tm2_ros2/blob/humble/doc/tm_humble.md
https://www.tm-robot.com/en/support/developer-area

中文快速提示
先自動讀取目前角度，再選一軸，例如 6，再填 +1，代表 J6 從現在加 1 度。
每次只改一軸，移除程式自訂角度增量限制；控制箱原有安全限制不變。
輸入角度增量後按 Enter 就送出，不再輸入 MOVE。送出前按 Ctrl+C 可取消。
關閉程式不會停止手臂；停止用操作棒，有危險按急停。


