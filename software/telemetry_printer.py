"""Displays all messages going via telemetry"""

from interfaces.telemetry.udp_reciever import TelemetryReciever
from interfaces.telemetry import udp_settings
import logging
import time

FORMAT = '[ %(levelname)s ] %(message)s'

def run():
	logging.basicConfig(format=FORMAT, level=logging.DEBUG)
	rx = TelemetryReciever(
		udp_settings.DEFAULT_PORT
	)

	while(1):
		time.sleep(0.0001)
		rx.update()


if __name__ == "__main__":
	run()
