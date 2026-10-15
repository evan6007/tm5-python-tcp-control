"""Read one TM EIH camera image via gRPC. No robot motion commands."""
if __name__ == "__main__":
    from camera_env import use_camera_environment
    use_camera_environment()

import argparse
import io
from datetime import datetime
from pathlib import Path
import sys

import grpc
from PIL import Image
from google.protobuf.empty_pb2 import Empty

sys.path.insert(0, str(Path(__file__).parent / "camera_api"))
import EIHCamera_pb2 as camera
import EIHCameraAPI_pb2 as api


def capture(ip):
    endpoint = f"{ip}:15567"
    print(f"Connecting to camera: {endpoint}", flush=True)
    with grpc.insecure_channel(endpoint, options=[
        ("grpc.max_receive_message_length", 32 * 1024 * 1024)
    ]) as channel:
        grpc.channel_ready_future(channel).result(timeout=5)

        def call(name, response):
            method = channel.unary_unary(
                f"/TmEIHCamera.EIHCameraApi/{name}",
                request_serializer=Empty.SerializeToString,
                response_deserializer=response.FromString,
            )
            return method(Empty(), timeout=10)

        state = call("isCameraConnected", api.isCameraConnectedResponse)
        print(f"Camera connected: {state.isCameraConnected}; {state.connection_message}")
        if not state.isCameraConnected:
            raise RuntimeError("Camera API is reachable, but the camera is not connected.")
        data = call("getImageData", camera.Camera.Image.Data).EncodeString
        with Image.open(io.BytesIO(data)) as frame:
            frame.load()
            folder = Path(__file__).parent / "camera_captures"
            folder.mkdir(exist_ok=True)
            path = folder / (datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".png")
            frame.save(path)
            print(f"Saved {frame.width} x {frame.height}: {path}")
            return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", default="192.168.1.101")
    args = parser.parse_args()
    try:
        capture(args.ip)
    except grpc.FutureTimeoutError:
        print("Camera API connection timed out. Check EIH Camera service, IP filter, and robot IP.")
        sys.exit(1)
    except (grpc.RpcError, RuntimeError, OSError, ValueError) as error:
        print(f"Capture failed: {error}")
        sys.exit(1)
