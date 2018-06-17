"""Handles serilization/deserialization of the UDP protocol to talk to the
robot. This protocol is stateless so the robot either knows what to do
or doesn't"""
from utils import compat, geom


DEFAULT_PORT = 45680


class RemoteControlPacket:
    def __init__(self, lin_vel, ang_vel, turret_elev, weapon_active, bullet_id):
        self.linear_velocity = lin_vel
        self.angular_velocity = ang_vel
        self.turret_elevation = turret_elev
        self.weapon_active = weapon_active
        self.bullet_id = bullet_id


PACKET_FORMAT = (
    "BB" +  # Header
    "ff" +  # Linear velocity x and y
    "f" +  # Angular Velocity
    "f" +  # Turrent elevation
    "B" + # weapon active
    "H" +  # Gun bullet ID
    "BB"  # Footer (potentially checksum)
)
PACKET_SIZE = compat.struct.calcsize(PACKET_FORMAT)


def serialize(packet):
    return compat.struct.pack(
        PACKET_FORMAT,
        0, 1,  # Header
        packet.linear_velocity.x,
        packet.linear_velocity.y,
        packet.angular_velocity,
        packet.turret_elevation,
        packet.weapon_active,
        packet.bullet_id % (2**16),
        0, 1  # Footer
    )


def deserialize(data):
    """Returns the packet or None if the supplied data is incorrect"""
    if len(data) != PACKET_SIZE:
        return None

    if data[0] != 0 or data[1] != 1 or data[-2] != 0 or data[-1] != 1:
        # Bade header or footer
        return None

    # Decode and Strip header
    raw = compat.struct.unpack(PACKET_FORMAT, data)[2:]

    return RemoteControlPacket(
        geom.Vec2(raw[0], raw[1]),
        raw[2],
        raw[3],
        bool(raw[4]),
        raw[5]
    )
