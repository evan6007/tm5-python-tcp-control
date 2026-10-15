"""Techman TCP protocol helper. Standard library only; no ROS or pip packages."""
import math
import socket
import struct
import time

SPEED_PERCENT = 3          # PTP command speed; does not change controller mode or speed settings


def packet(header, data):
    body = f"{header},{len(data.encode('ascii'))},{data},".encode("ascii")
    checksum = 0
    for byte in body:
        checksum ^= byte
    return b"$" + body + f"*{checksum:02X}\r\n".encode("ascii")


def receive(sock):
    deadline = time.monotonic() + 3

    def exact(size):
        result = b""
        while len(result) < size:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Packet receive timeout")
            sock.settimeout(remaining)
            part = sock.recv(size - len(result))
            if not part:
                raise ConnectionError("Robot disconnected")
            result += part
        return result

    header = b""
    while header.count(b",") < 2:
        header += exact(1)
        if len(header) > 64:
            raise ValueError("Packet header too long")
    name, size, _ = header.split(b",")
    if not name.startswith(b"$") or not 0 < int(size) < 65536:
        raise ValueError("Invalid packet length or header")
    data = exact(int(size))
    tail = exact(6)
    checksum = 0
    for byte in header[1:] + data + b",":
        checksum ^= byte
    if tail.upper() != f",*{checksum:02X}\r\n".encode("ascii"):
        raise ValueError("Packet checksum mismatch")
    return name, data


def decode_state(data):
    _, mode, binary = data.split(b",", 2)
    if mode != b"1":
        raise ValueError("Set the Ethernet Slave data table to Binary")
    fields = {}
    offset = 0
    while offset < len(binary):
        size = struct.unpack_from("<H", binary, offset)[0]
        offset += 2
        name = binary[offset:offset + size].decode("ascii")
        offset += size
        size = struct.unpack_from("<H", binary, offset)[0]
        offset += 2
        value = binary[offset:offset + size]
        offset += size
        if len(value) != size:
            raise ValueError("Incomplete state field")
        fields[name] = value
    if fields.get("Robot_Link") != b"\x01" or fields.get("Robot_Error") != b"\x00":
        raise RuntimeError("Robot disconnected, error active, or Robot_Link / Robot_Error fields missing")
    joints = list(struct.unpack("<6f", fields["Joint_Angle"]))
    if not all(math.isfinite(v) for v in joints):
        raise ValueError("Invalid joint angles")
    return joints


def read_joints(ip):
    with socket.create_connection((ip, 5891), timeout=3) as sock:
        header, data = receive(sock)
    if header != b"$TMSVR":
        raise ValueError("Expected an Ethernet Slave state packet")
    return decode_state(data)


def validate_target(current, target):
    if len(target) != 6 or not all(math.isfinite(v) for v in target):
        raise ValueError("Enter six finite numbers: J1 J2 J3 J4 J5 J6")


def move_joint(ip, joint, delta):
    if type(joint) is not int or not 1 <= joint <= 6:
        raise ValueError("Joint number must be an integer from 1 to 6")
    if not math.isfinite(delta):
        raise ValueError("Relative change must be a finite number")
    if delta == 0:
        print("Zero change; no motion command sent.")
        return
    before = read_joints(ip)
    target = before.copy()
    target[joint - 1] += delta
    validate_target(before, target)
    print(f"Fresh readback: J{joint} {before[joint - 1]:+.6f} -> {target[joint - 1]:+.6f} deg (change {delta:+g})")
    print("Only the selected joint changes; other targets come from live readback.")
    print(f"Command speed {SPEED_PERCENT}%; one move, no automatic return.")
    with socket.create_connection((ip, 5890), timeout=3) as sock:
        sock.sendall(packet("TMSTA", "00"))
        header, state = receive(sock)
        if header != b"$TMSTA" or state != b"00,true,Listen1":
            raise RuntimeError("Run PC_Control on the controller and enter Listen1 first")
        fresh = read_joints(ip)
        time.sleep(0.2)
        settled = read_joints(ip)
        if max(abs(a - b) for a, b in zip(fresh, settled)) > 0.01:
            raise RuntimeError("Robot is not stationary; no motion command sent")
        if max(abs(a - b) for a, b in zip(before, settled)) > 0.05:
            raise RuntimeError("Pose changed during preflight; read again and re-enter delta")
        # Build from the latest stationary sample, never from historical typed angles.
        target = settled.copy()
        target[joint - 1] += delta
        validate_target(settled, target)
        script = 'PTP("JPP",' + ','.join(f'{v:.6f}' for v in target)
        script += f',{SPEED_PERCENT},1000,0,false)'
        print("Sending ONCE:", script, flush=True)
        # Never retry automatically: timeout does not mean the command was not executed.
        sock.sendall(packet("TMSCT", "301," + script))
        header, reply = receive(sock)
        if header != b"$TMSCT" or reply != b"301,OK":
            raise RuntimeError(f"Unexpected acknowledgement: {header!r} {reply!r}; stop the project and inspect")
        print("Robot replied OK; waiting for joint readback.", flush=True)
        deadline = time.monotonic() + 300
        stable = 0
        while time.monotonic() < deadline:
            actual = read_joints(ip)
            stable = stable + 1 if max(abs(a - b) for a, b in zip(actual, target)) < 0.03 else 0
            if stable >= 3:
                print("Target confirmed by 3 consecutive readings (each joint error < 0.03 deg):", actual)
                return
            time.sleep(0.2)
        raise TimeoutError("Target not confirmed within 300 seconds. Press Robot Stick STOP. Do not blindly retry.")

