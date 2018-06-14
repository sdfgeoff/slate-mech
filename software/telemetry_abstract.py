"""Used to send data back to the operator"""

class TelemetryAbstract:
	LOG_ERROR = 0
	LOG_WARN = 1
	LOG_INFO = 2
	LOG_DEBUG = 3

	def send_log_message(self, log_level, string):
		"""Sends a textual message to the base-station"""
		print(string)


	def update(self):
		pass
