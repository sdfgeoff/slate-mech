import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import fixpath
import logging

from interfaces.telemetry.udp_reciever import TelemetryReciever
from interfaces.telemetry.udp_reciever import TelemetrySender
from interfaces.telemetry import udp_settings


def to_pixbuf(widget, stock):
    """Convert a GTK icon into a pixbuff"""
    val = widget.render_icon_pixbuf(stock, Gtk.IconSize.MENU)
    if val == None:
        logging.error("No Icon {}".format(stock))
    return val



class TelemetryHandler:
    """Routes the telemetry to the right place"""
    def __init__(self, builder):
        self.builder = builder

        self._telemetry = None

        self._log_window = self.builder.get_object('log_window')
        self._log_buffer = self._log_window.get_buffer()
        self._log_window.connect("size-allocate", self._autoscroll)

        self._status_window = self.builder.get_object('status_window')
        self._status_model = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf)
        self._setup_status_window()


        self.orange = self._log_buffer.create_tag("orange", foreground="orange")
        self.red = self._log_buffer.create_tag("red", foreground="red")
        self.green = self._log_buffer.create_tag("green", foreground="green")


        # Create a mapping dict for the message level codes to:
        #  - human readable text
        #  - text color
        #  - An icon
        w = self._status_window
        self._level_mapping = {
            TelemetrySender.CRITICAL: ["CRITICAL", self.red, to_pixbuf(w, 'gtk-stop')],
            TelemetrySender.ERROR: ["ERROR", self.red, to_pixbuf(w, 'gtk-dialog-error')],
            TelemetrySender.WARN: ["WARN", self.orange, to_pixbuf(w, 'gtk-dialog-warning')],
            TelemetrySender.INFO: ["INFO", None, None],
            TelemetrySender.DEBUG: ["DEBUG", None, None],
        }

        # Start the telemetry connection
        self.set_port(udp_settings.DEFAULT_PORT)

    def _setup_status_window(self):
        """Set up the columns in the status window"""
        self._status_window.set_model(self._status_model)

        for i, column in enumerate(["Var", "Val", "Status"]):
            if i == 2:
                cell = Gtk.CellRendererPixbuf()
                col = Gtk.TreeViewColumn(column, cell, pixbuf=2)
            else:
                cell = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(column, cell, text=i)
            self._status_window.append_column(col)

    def set_port(self, port):
        """Set what broadcast port the telemetry reciever is listeining to.
        Configures callbacks of the recivere to point at the right place"""
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
        """Runs whenever a new log message arrives"""
        start_iter = self._log_buffer.get_end_iter()
        name, format_tag, _icon = self._level_mapping[level]
        if format_tag is not None:
            self._log_buffer.insert_with_tags(
                start_iter, "[ {} ] {}\n".format(name, message),
                format_tag
            )
        else:
            self._log_buffer.insert(
                start_iter,
                "[ {} ] {}\n".format(name, message)
            )
        end_iter = self._log_buffer.get_end_iter()  # We just added to it...

    def _autoscroll(self, *args):
        """Scrolls the log window to the bottom"""
        # TODO: Test autoscroll
        scrolled_window = self._log_window.get_parent()
        adj = scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def var_val(self, var, val, level):
        """Runs whenever a new status var/val arrives"""
        _name, _tag, icon = self._level_mapping[level]
        for row_id, row in enumerate(self._status_model):
            if row[0] == var:
                row[1] = val
                row[2] = icon
                break
            if row[0] > var:
                # Todo test var:val ordering
                self._status_model.insert(row_id, [var, val, icon])
                break
        else:
            self._status_model.append([var, val, icon])

    def connection_changed(self, val):
        """Runs when the telemetry aquires or loses a connection"""
        label = self.builder.get_object('status_label')
        if val:
            label.set_text("Connected")
            start_iter = self._log_buffer.get_end_iter()
            self._log_buffer.insert_with_tags(
                start_iter, "-------- CONNECTED -------\n", self.green
            )

        else:
            label.set_text("Unable to find robot")
            start_iter = self._log_buffer.get_end_iter()
            self._log_buffer.insert_with_tags(
                start_iter, "----- CONNECTION LOST -----\n", self.red
            )

    def update(self):
        """Check for new telemetry messsages"""
        if self._telemetry is not None:
            self._telemetry.update()
