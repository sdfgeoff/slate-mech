"""Exposes robot control over a normal network
"""

from interfaces.remote_control.abstract import RemoteControlRecieverAbstract
from . import udp_protocol
import socket
import bot_math


class RemoteControlSender():
    def __init__(self, target_address):
        self.target_address = target_address
        self.packet = udp_protocol.RemoteControlPacket(
            bot_math.Vec2(0, 0),
            0,
            0,
            False,
            0,
        )

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

    def fire(self):
        self.packet.bullet_id += 1

    def update(self):
        data = udp_protocol.serialize(self.packet)
        self.socket.sendto(data, self.target_address)

