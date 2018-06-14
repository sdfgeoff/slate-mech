import compat
import bot_math

RemoteControlPacket = compat.collections.namedtuple("RemoteControlPacket", (
	"linear_velocity",
	"angular_velocity",
	"turret_elevation",
	"bullet_id",
))

PACKET_FORMAT = (
	"BB" +  # Header
	"ff" +  # Linear velocity x and y
	"f" +  # Angular Velocity
	"f" +  # Turrent elevation
	"h" + # Gun bullet ID
	"BB" # Footer (potentially checksum)
)
PACKET_SIZE = compat.struct.calcsize(PACKET_FORMAT)




def serialize(packet):
	return compat.struct.pack(
		PACKET_FORMAT,
		0,1, # Header
		packet.linear_velocity.x,
		packet.linear_velocity.y,
		packet.angular_velocity,
		packet.turret_elevation,
		packet.bullet_id,
		0,1 # Footer
	)


def deserialize(data):
	"""Returns the packet or None if the supplied data is incorrect"""
	assert len(data) == PACKET_SIZE

	if data[0] != 0 or data[1] != 1 or data[-2] != 0 or data[-1] != 1:
		# Bade header or footer
		return None

	raw = compat.struct.unpack(PACKET_FORMAT, data)[2:] # Decode and Strip header
	print(data)
	return RemoteControlPacket(
		bot_math.Vec2(raw[0], raw[1]),
		raw[2],
		raw[3],
		raw[4],
	)
