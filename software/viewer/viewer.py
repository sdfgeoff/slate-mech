import cv2
import numpy as np
import gi
import os
import time
import fixpath
from interfaces.telemetry.udp_reciever import TelemetryReciever
from interfaces.telemetry import udp_settings

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import logging


FORMAT = '[ %(levelname)s ] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class LogWindow(logging.Handler):
    def __init__(self, window):
        self.window = window
        super().__init__()

    def emit(self, record):
        buff = self.window.get_buffer()
        end = buff.get_end_iter()
        buff.insert(end, "[ {} ] {}\n".format(record.levelname, record.msg))
        end = buff.get_end_iter()  # We just added to it...
        self.window.scroll_to_iter(end, 0.0, False, 0, 1.0)



class ControlPanel:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("layout.glade")

        self.camera = None
        self.camera_id_changed(self.builder.get_object("selected_camera"))

        self.image = self.builder.get_object("camera_video")
        self.builder.connect_signals(self)

        self.telemetry = TelemetryReciever(
            udp_settings.DEFAULT_PORT
        )
        self.log = LogWindow(self.builder.get_object('log_window'))
        logging.getLogger().addHandler(self.log)

        window = self.builder.get_object("main_window")
        window.show_all()

        cam_frame = self.builder.get_object("cam_frame")
        cam_frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1, 0, 0))

        self.prev_frame_time = time.time()

        self.recorder = None

    def save_image(self, *args):
        got_frame, frame = self.camera.retrieve() # Get the previous frame
        if got_frame:
            filename = os.path.abspath("Image-{}.png".format(time.time()))
            self.builder.get_object("file_status").set_text("Saved image to {}".format(filename))
            cv2.imwrite(filename, frame)

    def record_video(self, widget):
        if self.recorder is not None:
            self.recorder.release()
            self.builder.get_object("file_status").set_text("Stopped recording")
            self.recorder = None

        if widget.get_active():
            # Start recording
            filename = os.path.abspath("Video-{}.avi".format(time.time()))
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            self.builder.get_object("file_status").set_text("Starting recording to {}".format(filename))
            self.recorder = cv2.VideoWriter(filename,fourcc, 30.0, (640,480))


    def close_window(self, *args):
        Gtk.main_quit(*args)
        print("Gone")

    def camera_id_changed(self, widget):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        adj = widget.get_adjustment()
        val = int(adj.get_value())
        self.camera = cv2.VideoCapture(val)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)



    def update(self, *args):
        got_frame, frame = self.camera.retrieve() # Get the current frame
        self.camera.grab() # Start capturing the next one while we're processing this one
        if got_frame:
            if self.recorder is not None:
                self.recorder.write(frame)
            self._display_image(frame)

            cur_time = time.time()
            fps = 1/(cur_time - self.prev_frame_time)
            self.builder.get_object('fps').set_text("Camera FPS: "+str(int(fps)))
            self.prev_frame_time = cur_time
        else:
            self._display_image(np.zeros((480,640,3), np.uint8))
            self.builder.get_object('fps').set_text("No Camera")

        self.telemetry.update()
        return True

    def _display_image(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Upscale to be big enough
        frame = cv2.resize(frame, None, fx=2, fy=2, interpolation = cv2.INTER_NEAREST)


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


panel = ControlPanel()
GLib.idle_add(panel.update)
Gtk.main()
