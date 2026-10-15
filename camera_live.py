"""Live TM camera preview. Run this file; press Q or Esc to close."""
if __name__ == "__main__":
    from camera_env import use_camera_environment
    use_camera_environment()

import io
import queue
import threading
import time
import tkinter as tk

from PIL import Image, ImageTk
from camera import grpc, Empty, camera

ROBOT_IP = "192.168.1.101"


def main():
    window = tk.Tk()
    window.title("TM Camera - Q / Esc to close")
    view = tk.Label(window, text="Connecting to camera...", width=100, height=30)
    view.pack()
    frames = queue.Queue(maxsize=1)
    stopped = threading.Event()
    channel = grpc.insecure_channel(
        f"{ROBOT_IP}:15567",
        options=[("grpc.max_receive_message_length", 32 * 1024 * 1024)],
    )
    get_image = channel.unary_unary(
        "/TmEIHCamera.EIHCameraApi/getImageData",
        request_serializer=Empty.SerializeToString,
        response_deserializer=camera.Camera.Image.Data.FromString,
    )

    def receive():
        count = 0
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            while not stopped.is_set():
                data = get_image(Empty(), timeout=10).EncodeString
                with Image.open(io.BytesIO(data)) as source:
                    frame = source.convert("RGB")
                frame.thumbnail((960, 720), Image.Resampling.BILINEAR)
                if frames.full():
                    try:
                        frames.get_nowait()
                    except queue.Empty:
                        pass
                frames.put_nowait(frame)
                count += 1
                if count in (1, 30):
                    print(f"Received frame {count}: {frame.width} x {frame.height}", flush=True)
        except Exception as error:
            if not stopped.is_set():
                print(f"Camera stopped: {type(error).__name__}: {error}", flush=True)
                errors.append("Camera disconnected. Check EIH Camera service and restart.")

    errors = []
    display_times = []

    def refresh():
        if errors:
            window.title(errors[0])
        try:
            frame = frames.get_nowait()
            view.image = ImageTk.PhotoImage(frame)
            view.configure(image=view.image, text="", width=0, height=0)
            display_times.append(time.perf_counter())
            del display_times[:-20]
            if len(display_times) > 1 and not errors:
                fps = (len(display_times) - 1) / (display_times[-1] - display_times[0])
                window.title(f"TM Camera - {fps:.1f} FPS - Q / Esc to close")
        except queue.Empty:
            pass
        window.after(10, refresh)

    def close(event=None):
        stopped.set()
        channel.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", close)
    for key in ("<Escape>", "q", "Q"):
        window.bind(key, close)
    threading.Thread(target=receive, daemon=True).start()
    refresh()
    window.mainloop()


if __name__ == "__main__":
    main()
