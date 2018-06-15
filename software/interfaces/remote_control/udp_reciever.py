"""Exposes robot control over a normal network (eg wifi, ethernet). Useful
for simulation and in-house testing
"""

from interfaces.remote_control.abstract import RemoteControlRecieverAbstract
from . import udp_protocol
from compat import socket, time
import bot_math

class RemoteControlReciever(RemoteControlRecieverAbstract):
    BINDING_TIMEOUT = 5.0  # Seconds until allows input from other source

    def __init__(self, telemetry, port):
        super().__init__()
        self.telemetry = telemetry
        self.telemetry.log(
            self.telemetry.INFO,
            "Opening Control Interface on port {}".format(port)
        )
        self.telemetry.var_val(
            "controller",
            "None",
            telemetry.CRITICAL
        )
        # The robot acts as a UDP server, and the controller connects to it
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.setblocking(False)

        self.controller = None

        self.last_packet = udp_protocol.RemoteControlPacket(
            bot_math.Vec2(0, 0),
            0,
            0,
            0
        )
        self.last_recieved_time = time.time()

    def get_linear_velocity(self):
        """Returns the target linear velocity that the user is requesting
        the bot to do"""
        return self.last_packet.linear_velocity

    def get_rotate_velocity(self):
        """Returns the speed which the robot should rotate at."""
        return self.last_packet.angular_velocity

    def get_gun_elevation(self):
        """Returns the change in gun elevation."""
        return self.last_packet.turret_elevation

    def get_bullet_id(self):
        """Returns a number that represents the shot count. This is to prevent
        the same "fire" signal from shooting multiple projectiles. The gun will
        only fire if this is different to the previous value. For non-auto, the
        controller increments it once. For full-auto, it can be a running
        counter as the exact value does not matter"""
        return self.last_packet.bullet_id

    def time_since_update(self):
        """Return the time in seconds since a control packet was sucessfully
        received"""
        return time.time() - self.last_recieved_time


    def update(self):
        """Updates all the values"""
        cur_time = time.time()

        # Get the latest data from the socket:
        data = None
        while True:
            try:
                data = self.socket.recvfrom(1024)
            except:
                break

        # If we got data, check who it came from and parse it
        if data is not None:
            message, address = data
            new_controller = False
            if self.controller is None:
                # Asssumes all incomming data is valid, so will bind to
                # any source of data
                self.telemetry.log(  # This should be general telemetry, not log
                    self.telemetry.INFO,
                    "Controller accepting connection from: {}".format(address)
                )
                self.telemetry.var_val(
                    "controller",
                    address,
                    self.telemetry.INFO
                )
                new_controller = True
                self.controller = address

            if self.controller != address:
                # Something else sent a message
                return

            new_packet = udp_protocol.deserialize(message)
            if new_packet is not None:
                self.last_packet = new_packet
                self.last_recieved_time = cur_time
                if new_controller:
                    self.on_controller_connected.call()
            else:
                # Bad Packet
                if new_controller:
                    self.telemetry.log(
                        self.telemetry.WARN,
                        "New controller gave bad packet. Disconnecting".format(repr(message))
                    )
                    self.controller = None
                else:
                    self.telemetry.log(
                        self.telemetry.WARN,
                        "Controller got bad packet: {}".format(repr(message))
                    )


        if self.controller is not None:
            # Handle Disconnects
            if self.last_recieved_time + self.BINDING_TIMEOUT < cur_time:
                self.telemetry.log(
                        self.telemetry.WARN,
                        "Controller connection from {} timed out".format(self.controller)
                    )
                self.on_controller_disconnected.call()
                self.controller = None
                self.telemetry.var_val(
                    "controller",
                    "None",
                    self.telemetry.CRITICAL
                )



