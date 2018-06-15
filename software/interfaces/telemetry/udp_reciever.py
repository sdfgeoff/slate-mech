import socket
from interfaces.telemetry.udp_sender import TelemetrySender
from . import udp_settings
import utils
import time
import logging

class TelemetryReciever:
    JITTER = 0.2  # Allowable timing jitter for pings from robot
    TIMEOUT = udp_settings.PING_TIME + JITTER

    def __init__(self, port):
        self.on_log = utils.FunctionList()
        self.on_var_val = utils.FunctionList()
        self.on_connect = utils.FunctionList()

        broadcast_address =self._get_broadcast_address()
        logging.info("Listening for robot telemetry {}".format(broadcast_address))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((broadcast_address, port))
        self.socket.setblocking(False)


        self.last_message_time = 0
        self._connected = False

        self.host = ''

    def update(self):
        data = True
        while data:
            try:
                recv = self.socket.recvfrom(1024)
            except:
                data = False
            else:
                message, host = recv
                self.last_message_time = time.time()

                if self.has_connection and not self._connected:
                    self.on_connect.call(True)
                    self._connected = self.has_connection

                self.handle_message(message)

                if self.host != host:
                    self.host = host
                    logging.info("Receiving From {}".format(host))

        if not self.has_connection and self._connected:
            self.on_connect.call(False)
            self._connected = self.has_connection





    def handle_message(self, message_bytes):
        message = message_bytes.decode('utf-8')
        message_type = int(message[0])
        message_level = int(message[1])
        message_contents = message[2:]

        if message_type == TelemetrySender.KEEP_ALIVE:
            # No action if it's just a keep-alive
            return
        elif message_type == TelemetrySender.LOG:
            self.on_log.call(message_level, message_contents)
        elif message_type == TelemetrySender.VAR_VAL:
            var, val = message_contents.split('\0x01', maxsplit=1)
            self.on_var_val.call(var, val, message_level)

    @property
    def has_connection(self):
        """Returns True if has recieved a keep-alive within expected time"""
        return self.last_message_time + self.TIMEOUT > time.time()


    def _get_broadcast_address(self):
        return '255.255.255.255'

