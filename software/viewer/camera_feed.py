import os
import cv2
import time
import numpy as np
import pathlib
import cairo

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf


WIDTH = 640
HEIGHT = 480

FPS_SMOOTHING = 0.8

# Frame to display when no camera available
NULL_FRAME = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class CameraFeed:
    def __init__(self, builder):
        self.builder = builder
        self.camera = None

        cam_selector = self.builder.get_object("selected_camera")
        self.camera_id_changed(cam_selector)

        self.image = self.builder.get_object("camera_video")
        self.image.connect("size-allocate", self.set_video_size)

        self.prev_frame_time = time.time()

        self.recorder = None
        self.raw_frame = None
        self.fps = 0
        
        self.vid_size = (640, 480)

    def camera_id_changed(self, widget):
        adj = widget.get_adjustment()
        val = int(adj.get_value())
        self.set_camera_id(val)

    def set_camera_id(self, camera_id):
        if self.camera is not None and not isinstance(self.camera, str):
            self.camera.release()
            self.camera = None

        if camera_id == -1:
            print("Switching to simulation")
            self.camera = "Simulation"
        else:
            self.camera = cv2.VideoCapture(camera_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
            
    def _update_simulation_cam(self):
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
        got_frame, frame = self.camera.retrieve()
        self.camera.grab()  # Start capturing the next one
        if got_frame:
            return frame

    def set_video_size(self, _img, rect):
        max_height = rect.height
        max_width = rect.width
        
        x_scale = max_width / WIDTH
        y_scale = max_height / HEIGHT
        scale = min(x_scale, y_scale)
        
        self.vid_size = (int(WIDTH * scale), int(HEIGHT * scale))
        
    def update(self):
        """Update the camera feed"""
        # Get the current frame and start capturing the next one
        
        if self.camera == "Simulation":
            self.raw_frame = self._update_simulation_cam()
        else:
            self.raw_frame = self._read_actual_cam()

        if self.raw_frame is not None:
            if self.recorder is not None:
                self.recorder.write(self.raw_frame)
            self._display_image(self.raw_frame)
            self._update_fps()
        else:
            self._display_image(NULL_FRAME)
            self.builder.get_object('fps').set_text("No Camera")

    def _update_fps(self):
        """Updates the FPS counter"""
        cur_time = time.time()
        fps = 1/(cur_time - self.prev_frame_time)
        
        self.fps = self.fps * FPS_SMOOTHING + fps * (1 - FPS_SMOOTHING)
        self.builder.get_object('fps').set_text("FPS: "+str(int(self.fps)))
        self.prev_frame_time = cur_time
        
    def _display_image(self, frame):
        """Display the current camera frame on the display"""
        # Upscale to be big enough
        # TODO: This only ever makes things bigger
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        wid, hei = self.vid_size
        
        # ~ frame = cv2.resize(  # faster at BILINEAR scaling
            # ~ frame, None, #(wid, hei),
            # ~ fx=scale, fy=scale,
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
            GdkPixbuf.InterpType.NEAREST
        )
        self.image.set_from_pixbuf(pb)


    def _generate_fullpath(self, base_name, file_format):
        home_dir = pathlib.Path.home()
        filename = base_name + time.strftime("%y-%m-%d %H:%M:%S") 
        filename += file_format
        full_path = home_dir / filename
        print(full_path)
        
        return str(full_path)

    def save_image(self, *args):
        """Dumps previous camera frame to a file"""
        if self.raw_frame is not None:
            filename = self._generate_fullpath("Image", ".png")
            self.builder.get_object("file_status").set_text(
                "Saved image to {}".format(filename)
            )
            cv2.imwrite(filename, self.raw_frame)
        else:
            self.builder.get_object("file_status").set_text(
                "No Image?"
            )

    def record_video(self, widget):
        """Toggles recording camera feed to a file"""
        if self.recorder is not None:
            self.recorder.release()
            self.builder.get_object("file_status").set_text(
                "Stopped recording"
            )
            self.recorder = None

        if widget.get_active():
            # Start recording
            filename = self._generate_fullpath("Video", ".avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            print("HERE")
            self.builder.get_object("file_status").set_text(
                "Starting recording to {}".format(filename)
            )
            self.recorder = cv2.VideoWriter(
                filename, fourcc,
                30.0,  # FPS
                (WIDTH, HEIGHT)
            )
            print("THERE")

    def close(self):
        if self.recorder is not None:
            self.recorder.release()
