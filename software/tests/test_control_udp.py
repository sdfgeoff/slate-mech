import pytest
import fixpath
from utils import compat, geom
from interfaces.remote_control import udp_protocol


def test_encode_decode():
    packet = udp_protocol.RemoteControlPacket(
        geom.Vec2(1, 2),
        3,
        4,
        False,
        5
    )

    data = udp_protocol.serialize(packet)
    recovered = udp_protocol.deserialize(data)
    assert recovered.linear_velocity.x == 1
    assert recovered.linear_velocity.y == 2
    assert recovered.angular_velocity == 3
    assert recovered.turret_elevation == 4
    assert recovered.weapon_active == False
    assert recovered.bullet_id == 5


def test_dicard_bad():
    assert udp_protocol.deserialize(b'asdf') == None
    assert udp_protocol.deserialize(b'f'*udp_protocol.PACKET_SIZE) == None


if __name__ == "__main__":
    pytest.main()
