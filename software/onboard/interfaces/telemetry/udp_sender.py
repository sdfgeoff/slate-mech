"""Since telemetry doesn't have to be reliable, it's being sent via
UDP broadcast to anything on the network.

Broadcast means that it doesn't have to know if there is something recieving
or not."""
from utils.compat import time, socket
from interfaces.telemetry.abstract import TelemetrySenderAbstract
from . import udp_settings


class TelemetrySender(TelemetrySenderAbstract):
    """Send telemetry data over UDP broadcast"""
    PING_TIME = udp_settings.PING_TIME  # Time between keep-alive pings

    # Packet Types
    KEEP_ALIVE = 0
    LOG = 1
    VAR_VAL = 2

    def __init__(self, port=udp_settings.DEFAULT_PORT):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.last_send_time = time.time()

    def log(self, log_level, message):
        """Send a logging message (probably to tell the user why the
        robot failed"""
        self._send(self.LOG, log_level, message)

    def _send(self, msg_type, level, message):
        """Send raw data"""
        self.socket.sendto(
            "{}{}{}".format(msg_type, level, message).encode('utf-8'),
            self._get_broadcast_address()
        )
        self.last_send_time = time.time()

    def var_val(self, varname, val, status=None):
        """Transmit a variable:value pair. The optional status allows
        the reciving program to know if the value is in an acceptable range
        or not"""
        if status is None:
            status = self.INFO
        self._send(self.VAR_VAL, status, "{}\0x01{}".format(varname, val))

    def _get_broadcast_address(self):
        """Figure out where to broadcast to"""
        return socket.getaddrinfo('255.255.255.255', self.port)[0][-1]

    def update(self):
        """Ensure keep-alives are sent so anything listening can tell
        if the robot goes down"""
        cur_time = time.time()
        if self.last_send_time + self.PING_TIME < cur_time:
            self._send(self.KEEP_ALIVE, cur_time, "")
