import os
import cv2
import time
import numpy as np
import pathlib
import threading
import queue

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf


WIDTH = 640
HEIGHT = 480

FPS_SMOOTHING = 0.8

# Frame to display when no camera available
NULL_FRAME = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

class BaseCamera(threading.Thread):
    """
    This thread handles reading from the camera, so that it can
    happen as fast as possible without interferring with anything else
    """
    def __init__(self, output_queue):
        super().__init__()
        self.daemon = True
        self.out = output_queue

        self.camera = None

        self._cam_id = None
        self._new_id = None
        self.killed = False

        self._target_image_filename = ""
        self._save_image = False

        self._target_video_filename = ""
        self._record_video = False
        self.recorder = None

    def set_id(self, new_id):
        """Non-threaded function to allow changing the active camera.
        One more frame of the current camera will be shown"""
        # Non-Threaded
        self._new_id = new_id

    def _update_simulation_cam(self):
        """Reads from a simulated camera (id=-1)"""
        frame = None
        if os.path.exists('/dev/shm/simulator/'):
            files = os.listdir('/dev/shm/simulator/')
            files = [f for f in files if f.find('stream') != -1]
            files.sort()
            if files:
                filename = '/dev/shm/simulator/'+files[0]
                frame = cv2.imread(filename)
                return frame

    def _read_actual_cam(self):
        """Reads from a normal webcam"""
        got_frame, frame = self.camera.read() # Start capturing the next one
        if got_frame:
            return frame

    def _update_cam_id(self):
        """Sets the active camera id from inside the thread. To access
        this outside the thread, use set_id()"""
        if self.camera is not None and not isinstance(self.camera, str):
            self.camera.release()
            self.camera = None

        if self._cam_id == -1:
            print("Switching to simulation")
            self.camera = "Simulation"
        else:
            self.camera = cv2.VideoCapture(self._cam_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


    def run(self):
        """Polls the camera as fast as possible"""
        while not self.killed:
            if self._cam_id != self._new_id:
                self._cam_id = self._new_id
                self._update_cam_id()

            if self.camera == "Simulation":
                raw_frame = self._update_simulation_cam()
            elif self.camera != None:
                raw_frame = self._read_actual_cam()
            else:
                raw_frame = None
                time.sleep(0.1)

            if raw_frame is not None:
                self.out.put(raw_frame)
                if self._save_image:
                    self._save_image = False
                    cv2.imwrite(self._target_image_filename, raw_frame)
                if self._record_video:
                    if self.recorder is None:
                        fourcc = cv2.VideoWriter_fourcc(*'H264')
                        self.recorder = cv2.VideoWriter(
                            self._target_video_filename, fourcc,
                            60.0,  # FPS
                            (WIDTH, HEIGHT)
                        )
                    self.recorder.write(raw_frame)

                else:
                    if self.recorder is not None:
                        self.recorder.release()
                        self.recorder = None

    def save_image(self, filename):
        self._target_image_filename = filename
        self._save_image = True

    def record_video(self, filename):
        """filename or None"""
        if filename == None:
            self._record_video = False
        else:
            self._target_video_filename = filename
            self._record_video = True



    def kill(self):
        self.killed = True



class CameraFilter(threading.Thread):
    def __init__(self, inqueue, outqueue):
        """Filters the image for display (eg image scaling)"""
        super().__init__()
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.killed = False

        self.vid_size = (640, 480)

    def set_vid_size(self, size):
        # WARNING: not actually thread-save
        self.vid_size = size

    def run(self):
        while not self.killed:
            try:
                frame = self.inqueue.get(True, 0.1)
            except queue.Empty:
                pass
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                wid, hei = self.vid_size

                # ~ frame = cv2.resize(  # faster at BILINEAR scaling
                    # ~ frame, None, (wid, hei),
                    # ~ interpolation=cv2.INTER_LINEAR
                # ~ )

                bytes1 = frame.tobytes()
                bytes2 = GLib.Bytes(bytes1)

                pb = GdkPixbuf.Pixbuf.new_from_bytes(
                    bytes2,
                    GdkPixbuf.Colorspace.RGB,
                    False,
                    8,
                    WIDTH,
                    HEIGHT,
                    WIDTH*3
                )
                pb = pb.scale_simple(  # Faster at NEAREST scaling
                    wid, hei,
                    GdkPixbuf.InterpType.BILINEAR
                )
                self.outqueue.put(pb)

    def kill(self):
        self.killed = True




class CameraFeed:
    def __init__(self, builder):
        self.builder = builder

        self.cam_queue = queue.Queue()
        self.filter_queue = queue.Queue()

        self.camera = BaseCamera(self.cam_queue)
        self.camera.start()

        self.filter = CameraFilter(self.cam_queue, self.filter_queue)
        self.filter.start()

        self.image = self.builder.get_object("camera_video")
        self.image.connect("size-allocate", self.set_video_size)

        self.fps = 0
        self.prev_frame_time = time.time()


        cam_selector = self.builder.get_object("selected_camera")
        self.camera_id_changed(cam_selector)


    def camera_id_changed(self, widget):
        adj = widget.get_adjustment()
        val = int(adj.get_value())
        self.set_camera_id(val)

    def set_camera_id(self, camera_id):
        self.camera.set_id(camera_id)
        # This doenst always display because often an image is already
        # between the camera and display
        self.builder.get_object('fps').set_text("No Camera")

    def set_video_size(self, _img, rect):
        max_height = rect.height
        max_width = rect.width

        x_scale = max_width / WIDTH
        y_scale = max_height / HEIGHT
        scale = min(x_scale, y_scale)

        self.filter.set_vid_size(
            (int(WIDTH * scale), int(HEIGHT * scale))
        )

    def update(self):
        """Update the camera feed"""
        # Get the current frame and start capturing the next one
        try:
            frame = self.filter_queue.get(False)
        except queue.Empty:
            return
        else:

            self._update_fps()
            self._display_image(frame)

    def _update_fps(self):
        """Updates the FPS counter"""
        cur_time = time.time()
        fps = 1/(cur_time - self.prev_frame_time)

        self.fps = self.fps * FPS_SMOOTHING + fps * (1 - FPS_SMOOTHING)
        self.builder.get_object('fps').set_text("FPS: "+str(int(self.fps)))
        self.prev_frame_time = cur_time

    def _display_image(self, frame):
        """Display the current camera frame on the display"""
        self.image.set_from_pixbuf(frame)


    def _generate_fullpath(self, base_name, file_format):
        home_dir = pathlib.Path.home()
        filename = base_name + time.strftime("%y-%m-%d %H:%M:%S")
        filename += file_format
        full_path = home_dir / filename

        return str(full_path)

    def save_image(self, *args):
        """Dumps previous camera frame to a file"""
        filename = self._generate_fullpath("Image", ".png")
        self.builder.get_object("file_status").set_text(
            "Saving image to {}".format(filename)
        )
        self.camera.save_image(filename)

    def record_video(self, widget):
        """Toggles recording camera feed to a file"""
        if widget.get_active():
            # Start recording
            filename = self._generate_fullpath("Video", ".avi")
            self.builder.get_object("file_status").set_text(
                "Starting recording to {}".format(filename)
            )
            self.camera.record_video(filename)
        else:
            self.builder.get_object("file_status").set_text(
                "Stopping recording"
            )
            self.camera.record_video(None)


    def close(self):
        self.camera.kill()
        self.filter.kill()
        self.camera.join()
        self.filter.join()


