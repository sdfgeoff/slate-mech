import logging
import socket
import telemetry_udp_broadcast
import time

class TelemetryReciever:
	MAPPING = {
		telemetry_udp_broadcast.TelemetryUdpBroadcast.LOG_WARN: logging.warning,
		telemetry_udp_broadcast.TelemetryUdpBroadcast.LOG_ERROR: logging.error,
		telemetry_udp_broadcast.TelemetryUdpBroadcast.LOG_INFO: logging.info,
		telemetry_udp_broadcast.TelemetryUdpBroadcast.LOG_DEBUG: logging.debug,
	}
	JITTER = 0.2  # Allowable timing jitter for pings from robot
	TIMEOUT = telemetry_udp_broadcast.TelemetryUdpBroadcast.PING_TIME + JITTER

	def __init__(self, port):
		broadcast_address =self._get_broadcast_address()
		logging.info("Listening for robot telemetry {}".format(broadcast_address))
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.socket.bind((broadcast_address, port))
			self.socket.setblocking(False)
		except Exception as err:
			self.active = False
			logging.error("Unable to listen to broadcast due to: {}".format(err))
		else:
			self.active = True

		self.last_message_time = time.time()
		self.last_message_display_time = time.time()
		
		self.host = ''

	def update(self):
		if not self.active:
			return

		cur_time = time.time()
		try:
			recv = self.socket.recvfrom(1024)
		except:
			pass
		else:
			message, host = recv
			message = message.decode('utf-8')
			data = message.split(':', maxsplit=1)
			try:
				log_func = self.MAPPING.get(int(data[0]))
			except (IndexError, ValueError):
				logging.warn("Unknown log level {}".format(data[0]))

			else:
				if self.host != host:
					self.host = host
					logging.info("Receiving From {}".format(host))
				self.last_message_time = cur_time
				self.last_message_display_time = cur_time

				log_func(data[1])


		if self.last_message_display_time + self.TIMEOUT < cur_time:
			self.last_message_display_time = cur_time
			logging.critical(
				"No message from robot for {} seconds".format(
					round(cur_time - self.last_message_time, 1)
				)
			)



	def _get_broadcast_address(self):
		return '255.255.255.255'


if __name__ == "__main__":
	FORMAT = '[ %(levelname)s ] %(message)s'
	logging.basicConfig(format=FORMAT, level=logging.DEBUG)
	rx = TelemetryReciever(telemetry_udp_broadcast.DEFAULT_PORT)
	while(1):
		time.sleep(0.0001)
		rx.update()
