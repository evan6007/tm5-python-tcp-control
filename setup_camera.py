"""Install camera dependencies in an isolated local environment. No robot connection."""
from pathlib import Path
import subprocess
import sys
import venv


def main():
    if sys.platform != "win32" or sys.version_info < (3, 9):
        raise SystemExit("This installer requires Windows and Python 3.9 or newer.")
    root = Path(__file__).resolve().parent
    environment = root / ".venv-camera"
    interpreter = environment / "Scripts" / "python.exe"
    if not interpreter.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    subprocess.run([str(interpreter), "-m", "pip", "install", "-r",
                    str(root / "requirements-camera.txt")], check=True)
    subprocess.run([str(interpreter), "-c",
                    "import tkinter, grpc, PIL; import camera; import camera_live; "
                    "print('Camera dependencies and protocol imports: OK')"],
                   cwd=root, check=True)
    print("Ready. Run: python camera.py  OR  python camera_live.py")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
