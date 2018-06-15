"""Since telemetry doesn't have to be reliable, it's being sent via
UDP broadcast to anything on the network"""
from compat import time, socket
from interfaces.telemetry.abstract import TelemetrySenderAbstract
from . import udp_settings

class TelemetrySender(TelemetrySenderAbstract):
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
        self.send(self.LOG, log_level, message)


    def send(self, msg_type, level, message):
        self.socket.sendto(
            "{}{}{}".format(msg_type, level, message).encode('utf-8'),
            self._get_broadcast_address()
        )
        self.last_send_time = time.time()


    def var_val(self, varname, val, status=None):
        if status is None:
            status = self.INFO
        self.send(self.VAR_VAL, status, "{}\0x01{}".format(varname, val))

    def _get_broadcast_address(self):
        return socket.getaddrinfo('255.255.255.255', self.port)[0][-1]

    def update(self):
        cur_time = time.time()
        if self.last_send_time + self.PING_TIME < cur_time:
            self.send(self.KEEP_ALIVE, cur_time, "")
