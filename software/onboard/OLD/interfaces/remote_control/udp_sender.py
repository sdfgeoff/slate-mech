"""Exposes robot control over a normal network
"""

from interfaces.remote_control.udp_reciever import RemoteControlReciever
from interfaces.remote_control import udp_protocol
from . import udp_protocol
import socket
from utils import geom


class RemoteControlSender():
    def __init__(self, target_port=udp_protocol.DEFAULT_PORT):
        self.port = target_port
        self.packet = udp_protocol.RemoteControlPacket(
            geom.Vec2(0, 0),
            0,
            0,
            False,
            0,
        )

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setblocking(False)


    def fire(self):
        self.packet.bullet_id += 1

    def set_linear_velocity(self, velocity):
        self.packet.linear_velocity.x = velocity.x
        self.packet.linear_velocity.y = velocity.y

    def set_angular_velocity(self, velocity):
        self.packet.angular_velocity = velocity

    def set_turret_elevation(self, elevation):
        self.packet.turret_elevation = elevation

    def set_weapon_active(self, weapon_active):
        self.packet.weapon_active = weapon_active

    def get_weapon_active(self):
        return self.packet.weapon_active

    def _get_broadcast_address(self):
        """Figure out where to broadcast to"""
        return socket.getaddrinfo('255.255.255.255', self.port)[0][-1]

    def update(self):
        data = udp_protocol.serialize(self.packet)

        self.socket.sendto(
            data,
            self._get_broadcast_address()
        )



