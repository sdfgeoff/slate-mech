import os
import cv2
import time
import numpy as np

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf


WIDTH = 640
HEIGHT = 480

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

        # Black Background to make things "better"
        cam_frame = self.builder.get_object("cam_frame")
        cam_frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1, 0, 0))

        self.prev_frame_time = time.time()

        self.recorder = None

    def camera_id_changed(self, widget):
        adj = widget.get_adjustment()
        val = int(adj.get_value())
        self.set_camera_id(val)

    def set_camera_id(self, camera_id):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.camera = cv2.VideoCapture(camera_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def update(self):
        """Update the camera feed"""
        # Get the current frame and start capturing the next one
        got_frame, frame = self.camera.retrieve()
        self.camera.grab()  # Start capturing the next one
        if got_frame:
            if self.recorder is not None:
                self.recorder.write(frame)
            self._display_image(frame)

            cur_time = time.time()
            fps = 1/(cur_time - self.prev_frame_time)
            self.builder.get_object('fps').set_text("FPS: "+str(int(fps)))
            self.prev_frame_time = cur_time
        else:
            self._display_image(NULL_FRAME)
            self.builder.get_object('fps').set_text("No Camera")

    def _display_image(self, frame):
        """Display the current camera frame on the display"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Upscale to be big enough
        # TODO: This only ever makes things bigger
        max_height = self.image.get_allocation().height
        max_width = self.image.get_allocation().width

        x_scale = max_width / frame.shape[1]
        y_scale = max_height / frame.shape[0]
        scale = min(x_scale, y_scale)

        frame = cv2.resize(
            frame, None,
            fx=scale, fy=scale,
            interpolation=cv2.INTER_LINEAR
        )

        pb = GdkPixbuf.Pixbuf.new_from_data(
            frame.tostring(),
            GdkPixbuf.Colorspace.RGB,
            False,
            8,
            frame.shape[1],
            frame.shape[0],
            frame.shape[2]*frame.shape[1]
        )
        self.image.set_from_pixbuf(pb.copy())

    def save_image(self, *args):
        """Dumps previous camera frame to a file"""
        got_frame, frame = self.camera.retrieve()  # Get the previous frame
        if got_frame:
            filename = os.path.abspath("Image-{}.png".format(time.time()))
            self.builder.get_object("file_status").set_text(
                "Saved image to {}".format(filename)
            )
            cv2.imwrite(filename, frame)

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
            filename = os.path.abspath("Video-{}.avi".format(time.time()))
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            self.builder.get_object("file_status").set_text(
                "Starting recording to {}".format(filename)
            )
            self.recorder = cv2.VideoWriter(
                filename, fourcc,
                30.0,  # FPS
                (WIDTH, HEIGHT)
            )

    def close(self):
        if self.recorder is not None:
            self.recorder.release()
