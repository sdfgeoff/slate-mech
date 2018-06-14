from interfaces.remote_control import udp_protocol
import bot_math

start = udp_protocol.RemoteControlPacket(
	bot_math.Vec2(1.2, 4.5),
	7.5,
	0.2,
	5
)

data = udp_protocol.serialize(start)
print(data)


end = udp_protocol.deserialize(data)
print(end)
