"""Displays all messages going via telemetry"""
import fixpath

from interfaces.telemetry.udp_reciever import TelemetryReciever
from interfaces.telemetry.udp_sender import TelemetrySender
from interfaces.telemetry import udp_settings
import logging
import time

FORMAT = '[ %(levelname)s ] %(message)s'

MAPPING = {
    TelemetrySender.CRITICAL: logging.critical,
    TelemetrySender.ERROR: logging.error,
    TelemetrySender.WARN: logging.warning,
    TelemetrySender.INFO: logging.info,
    TelemetrySender.DEBUG: logging.debug
}

def log(level, message):
    funct = MAPPING[level]
    funct(message)

def var_val(var, val, level):
    funct = MAPPING[level]
    funct("VARVAL: {} = {}".format(var, val))


def run():
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    rx = TelemetryReciever(
        udp_settings.DEFAULT_PORT
    )
    rx.on_log.append(log)
    rx.on_var_val.append(var_val)

    while(1):
        time.sleep(0.0001)
        rx.update()
        if not rx.has_connection:
            print("No Telemetry from Robot")


if __name__ == "__main__":
    run()
