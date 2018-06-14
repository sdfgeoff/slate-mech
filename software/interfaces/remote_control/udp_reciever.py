"""Exposes robot control over a normal network (eg wifi, ethernet). Useful
for simulation and in-house testing
"""

from interfaces.remote_control.abstract import RemoteControlAbstract
from . import upd_protocol
from compat import socket, time
import bot_math

class RemoteControlReciever(RemoteControlRecieverAbstract):
	def __init__(self, telemetry, port):
		telemetry.send_log_message(
			telemetry.LOG_INFO,
			"Opening Control Interface on port {}".format(port)
		)
		# The robot acts as a UDP server, and the controller connects to it
		self.socket = socket.socket()

		self.last_packet =
		self.last_recieved = time.time()

	def update():
		pass
