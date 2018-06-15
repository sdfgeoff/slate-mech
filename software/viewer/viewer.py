import cv2
import numpy as np
import gi
import os
import time
import fixpath
from interfaces.telemetry.udp_reciever import TelemetryReciever
from interfaces.telemetry.udp_reciever import TelemetrySender
from interfaces.telemetry import udp_settings

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import logging

NULL_FRAME = np.zeros((480,640,3), np.uint8)


def to_pixbuf(widget, stock):
    return widget.render_icon_pixbuf(stock,Gtk.IconSize.MENU)


class TelemetryHandler:

    def __init__(self, port, builder):
        self.builder = builder

        self._telemetry = None

        self._log_window = self.builder.get_object('log_window')
        self._log_buffer = self._log_window.get_buffer()

        self._status_window = self.builder.get_object('status_window')
        self._status_model = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf)
        self._setup_status_window()


        self.orange = self._log_buffer.create_tag("orange", foreground="orange")
        self.red = self._log_buffer.create_tag("red", foreground="red")
        self.green = self._log_buffer.create_tag("green", foreground="green")

        w = self._status_window
        self._level_mapping = {
            TelemetrySender.CRITICAL: ["CRITICAL", self.red, to_pixbuf(w, 'gtk-stop')],
            TelemetrySender.ERROR: ["ERROR", self.red, to_pixbuf(w, 'dialog-error')],
            TelemetrySender.WARN: ["WARN", self.orange, to_pixbuf(w, 'dialog-warning')],
            TelemetrySender.INFO: ["INFO", None, None],
            TelemetrySender.DEBUG: ["DEBUG", None, None],
        }

        self.set_port(port)

    def _setup_status_window(self):
        self._status_window.set_model(self._status_model)

        for i, column in enumerate(["Var", "Val", "Status"]):
            # cellrenderer to render the text
            if i == 2:
                cell = Gtk.CellRendererPixbuf()
                col = Gtk.TreeViewColumn(column, cell, pixbuf=2)
                #col.set_cell_data_func(cell, self._status_icon)
            else:
                cell = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(column, cell, text=i)
            # and it is appended to the treeview
            self._status_window.append_column(col)


    def set_port(self, port):
        if self._telemetry is not None:
            self._telemetry.close()

        self._telemetry = TelemetryReciever(
            port
        )
        self._telemetry.on_log.append(self.log)
        self._telemetry.on_var_val.append(self.var_val)
        self._telemetry.on_connect.append(self.connection_changed)
        self.connection_changed(False)


    def log(self, level, message):
        start_iter = self._log_buffer.get_end_iter()
        name, format_tag, _icon = self._level_mapping[level]
        if format_tag is not None:
            self._log_buffer.insert_with_tags(start_iter, "[ {} ] {}\n".format(name, message), format_tag)
        else:
            self._log_buffer.insert(start_iter, "[ {} ] {}\n".format(name, message))
        end_iter = self._log_buffer.get_end_iter()  # We just added to it...

        #TODO: This doesn't work properly:
        self._log_window.scroll_to_iter(end_iter, 0.0, False, 0, 1.0)

    def var_val(self, var, val, level):
        _name, _tag, icon = self._level_mapping[level]
        for row_id, row in enumerate(self._status_model):
            if row[0] == var:
                row[1] = val
                row[2] = icon #Gtk.GtkPixbuf()
                break
            if row[0] > var:
                self._status_model.insert(row_id, [var, val, icon])
                break
        else:
            self._status_model.append([var, val, icon])

    def connection_changed(self, val):
        label = self.builder.get_object('status_label')
        if val:
            label.set_text("Connected")
            start_iter = self._log_buffer.get_end_iter()
            self._log_buffer.insert_with_tags(start_iter, "-------- CONNECTED -------\n", self.green)

        else:
            label.set_text("Unable to find robot")
            start_iter = self._log_buffer.get_end_iter()
            self._log_buffer.insert_with_tags(start_iter, "----- CONNECTION LOST -----\n", self.red)


    def update(self):
        if self._telemetry is not None:
            self._telemetry.update()




class ControlPanel:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("layout.glade")

        self.camera = None
        self.camera_id_changed(self.builder.get_object("selected_camera"))

        self.image = self.builder.get_object("camera_video")
        self.builder.connect_signals(self)


        self.telemetry = TelemetryHandler(
            udp_settings.DEFAULT_PORT,
            self.builder
        )

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
        if self.recorder is not None:
            self.recorder.release()
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
            self._display_image(NULL_FRAME)
            self.builder.get_object('fps').set_text("No Camera")

        self.telemetry.update()
        return True

    def _display_image(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Upscale to be big enough
        # TODO: This only ever makes things bigger
        max_height = self.image.get_allocation().height
        max_width = self.image.get_allocation().width

        x_scale = max_width / frame.shape[1]
        y_scale = max_height / frame.shape[0]
        scale = min(x_scale, y_scale)

        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)

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
