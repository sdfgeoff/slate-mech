import connection
import time
import machine

connection.init()

joy1x = machine.ADC(machine.Pin(36))
joy1y = machine.ADC(machine.Pin(37))
joy2x = machine.ADC(machine.Pin(38))
joy2y = machine.ADC(machine.Pin(39))

while(1):
    # ~ latest = connection.get_latest_packet()
    # ~ if latest is not None:
        # ~ print(latest)
    # ~ else:
        # ~ time.sleep(0.5)
        # ~ print("Waiting")

