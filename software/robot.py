
class Robot:
	def __init__(self, telemetry, control_source, hardware):
		self.telemetry = telemetry

	def update(self):
		self.telemetry.update()
