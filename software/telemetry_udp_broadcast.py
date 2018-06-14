"""Since telemetry doesn't have to be reliable, it's being sent via
UDP broadcast to anything on the network"""
from compat import time, socket
from telemetry_abstract import TelemetryAbstract

DEFAULT_PORT = 45678

class TelemetryUdpBroadcast(TelemetryAbstract):
	PING_TIME = 1.0  # Time between keep-alive pings

	def __init__(self, port=DEFAULT_PORT):
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		self.last_send_time = time.time()

	def send_log_message(self, log_level, message):
		message = '{}:{}'.format(log_level, message)
		self.socket.sendto(
			message.encode('utf-8'),
			self._get_broadcast_address()
		)
		self.last_send_time = time.time()

	def _get_broadcast_address(self):
		return socket.getaddrinfo('255.255.255.255', self.port)[0][-1]

	def update(self):
		cur_time = time.time()
		if self.last_send_time + self.PING_TIME < cur_time:
			self.send_log_message(self.LOG_DEBUG, cur_time)
