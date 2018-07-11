import sys
from utils import compat
from brain import robot
from interfaces.telemetry.udp_sender import TelemetrySender
from interfaces.remote_control.udp_reciever import RemoteControlReciever
from interfaces.chassis.abstract import Chassis as Chassis
import network
import time

# ---------------------- Set up hardware --------------------------------------
# Create Network
ap = network.WLAN(network.AP_IF) # create access-point interface
ap.active(True)         # activate the interface
ap.config(essid='SlateMech', authmode=network.AUTH_OPEN) # set the ESSID of the access point


# ---------------- Create the components of the robot -------------------------
telemetry = TelemetrySender(45678)

# Send system information
telemetry.log(telemetry.INFO, "Robot Booting")
if compat.micro:
	telemetry.log(telemetry.INFO, "Running from Micropython")
else:
	telemetry.log(telemetry.INFO, "Running from Cpython")
telemetry.log(telemetry.INFO, "Running on {}".format(sys.platform))


control = RemoteControlReciever(telemetry)
chassis = Chassis()

main_robot = robot.Robot(
	telemetry,
	control,
	chassis
)

def mainloop():
	try:
		# Update the entire robot
		main_robot.update()
	except Exception as err:
		# Retrieve the problem and send it via telemetry
		records = compat.io.StringIO()
		if compat.micro:
			sys.print_exception(err, records)
		else:
			import traceback
			traceback.print_exception(*sys.exc_info(), file=records)
		records.seek(0)
		error_string = records.read()

		# Print first in case something is wrong with telemetry
		print(error_string)

		# Tell the user
		telemetry.log(telemetry.ERROR, repr(error_string))

		# Hope the problem resolves itself....
		compat.time.sleep(0.1)


calls = 0
def irq(timer):
	global calls
	calls += 1

import machine
maintick = machine.Timer(-1)
maintick.init(mode=maintick.PERIODIC, period=16, callback=irq)


time_delta = 0
prev_call_time = time.ticks_ms()
max_time = 0

while(1):
	if calls > 0:
		state = machine.disable_irq()
		calls -=1
		state = machine.enable_irq(state)

		now = time.ticks_ms()
		time_delta = now - prev_call_time
		prev_call_time = now

		if time_delta > max_time:
			max_time = time_delta
			print("Freq: " + str(1/time_delta * 1000))

		telemetry.var_val(
			"loop_time", time_delta,
			telemetry.INFO
		)

		mainloop()



