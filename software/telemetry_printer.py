"""Displays all messages going via telemetry"""

from interfaces import telemetry_udp_reciever
from interfaces import telemetry_udp_sender
import logging
import time

FORMAT = '[ %(levelname)s ] %(message)s'

def run():
	logging.basicConfig(format=FORMAT, level=logging.DEBUG)
	rx = telemetry_udp_reciever.TelemetryReciever(
		telemetry_udp_sender.DEFAULT_PORT
	)

	while(1):
		time.sleep(0.0001)
		rx.update()


if __name__ == "__main__":
	run()
