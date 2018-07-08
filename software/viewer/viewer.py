"""The viewer is the base-station of the robot, used to display the video
feed and telemetry. The video feed is routed into the camera as a normal
webcam using a module such as the Eachine ROTG02
This application prioritizes low latency on that video stream.
"""


import os
import time

import telemetry
import camera_feed
import control

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import logging
import cProfile


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class ControlPanel:
    """The main viewer window"""
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(BASE_PATH, "layout.glade"))

        # Can set port with the self.telemetry.set_port()
        self.telemetry = telemetry.TelemetryHandler(self.builder)
        self.camera_feed = camera_feed.CameraFeed(self.builder)
        self.control = control.Control(self.builder)

        self.builder.connect_signals({
            "save_image":self.camera_feed.save_image,
            "record_video":self.camera_feed.record_video,
            "camera_id_changed":self.camera_feed.camera_id_changed,
            "close_window":self.close_window
        })

        window = self.builder.get_object("main_window")
        window.show_all()

    def close_window(self, *args):
        """Ensures a video isn't being recorded, and then quits"""
        self.camera_feed.close()
        Gtk.main_quit(*args)

    def update(self, *args):
        """Runs every 8ms to update connections etc."""
        # WARNING: Big problems if a call takes >8 milliseconds
        self.control.update()
        self.camera_feed.update()
        self.telemetry.update()
        return True


def main():
    panel = ControlPanel()
    GLib.timeout_add(8, panel.update)
    Gtk.main()

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    pr.print_stats(sort='tottime')
