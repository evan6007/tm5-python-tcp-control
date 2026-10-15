"""Run: python control.py. Select ONE joint and a relative change in degrees."""
from tm_tcp import read_joints, move_joint

IP = "192.168.1.101"

if __name__ == "__main__":
    try:
        current = read_joints(IP)
        print("Live joint angles (degrees):")
        for number, angle in enumerate(current, 1):
            print(f"  J{number}: {angle:+.6f}")
        print("Choose joint 1-6, then enter +degrees or -degrees.")
        print("Example: 1 then +5 = J1 +5 degrees; 6 then -2 = J6 -2 degrees.")
        text = input("Joint [1-6] (Enter to exit): ").strip()
        if text:
            delta = float(input("Change [+/- degrees], e.g. +5 or -2 (Enter to move): "))
            move_joint(IP, int(text), delta)
    except (Exception, KeyboardInterrupt) as exc:
        print(f"Stopped: {exc}")
        print("Closing Python does NOT stop an issued motion. Use Robot Stick STOP; use E-stop in an emergency.")

