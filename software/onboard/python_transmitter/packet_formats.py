import struct


PACKET_TYPES = {}

def register_packet(id_byte=None): #id_byte=None):
    assert len(id_byte) == 1
    assert id_byte not in PACKET_TYPES
    def add_func(packet):
        PACKET_TYPES[id_byte] = packet
        packet.id_byte = id_byte
        return packet
    return add_func


@register_packet(id_byte=b'c')
class ControlPacket:
    PACK_STRING = "HHHH"
    id_byte = b'c'
    def __init__(self):
        self.val1 = 0
        self.val2 = 0
        self.val3 = 0
        self.val4 = 0

    def serialize(self):
        return struct.pack(
            self.PACK_STRING,
            self.val1,
            self.val2,
            self.val3,
            self.val4,
        )

    def deserialize(data):
        parsed = struct.unpack(self.PACK_STRING)
        self.val1 = parsed[0]
        self.val2 = parsed[1]
        self.val3 = parsed[2]
        self.val4 = parsed[3]
