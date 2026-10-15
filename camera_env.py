"""Use the project's camera environment when launched with another Python."""
from pathlib import Path
import subprocess
import sys


def use_camera_environment():
    environment = Path(__file__).resolve().parent / ".venv-camera"
    interpreter = environment / "Scripts" / "python.exe"
    if interpreter.is_file() and Path(sys.prefix).resolve() != environment.resolve():
        try:
            result = subprocess.run([str(interpreter), *sys.argv])
        except KeyboardInterrupt:
            raise SystemExit(130)
        raise SystemExit(result.returncode)
