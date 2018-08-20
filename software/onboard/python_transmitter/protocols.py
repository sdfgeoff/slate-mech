import connection
import struct

CONTROL_PACKET = b'c'
VAR_VAL_PACKET = b'v'


class ControlPacket:
    PACK_STRING = "H"
    def __init__(self, val):
        self.val = val

    def serialize():
        return struct.pack(
            self.PACK_STRING,
            self.val
        )

    def deserialize(data):
        parsed = struct.unpack(self.PACK_STRING)
        self.val = parsed[0]


def init():
    connection.init()

def handle_control_packet(packet):
    print("Got Control Packet:", packet)


def send_control_packet(control_packet):
    connection.send(CONTROL_PACKET + control_packet.serialize())


def handle_packet(packet):
    if packet[0] == CONTROL_PACKET_PREFIX:
        handle_control_packet(packet[1])
    else:
        print("Unknown packet type")


def update():
    packet = connection.get_latest_packet()
    while packet is not None:
        handle_packet(packet)
        packet = connection.get_latest_packet()

