"""Exposes robot control over network for json encoded packets. Each
packet should be ended by a newline eg:

{
	"velocity":[0, 0],
	"rotation":0,
	"elevation_delta":0,
	"fire":false
}
"""

from remote_control_abstract import RemoteControlAbstract
import bot_math
from compat import socket, time


class RemoteControlNetwork(RemoteControlAbstract):
	CONTROL_TIMEOUT = 1.0  # Time until resets the robot to "off"


	def __init__(self, telemetry, port):
		telemetry.send_log_message(
			telemetry.LOG_INFO,
			"Opening Control Interface on port {}".format(port)
		)
		# The robot acts as a UDP server, and the controller connects to it
		self.socket = socket.socket()

		self.last_recieved = time.time()

	def get_control_input():
		velocity = bot_math.Vec2(0, 0)
		rot = 0
		gun_elevation_delta = 0
		fire_gun = False
		return (
			velocity,
			rot,
			gun_elevation_delta,
			fire_gun,
		)
