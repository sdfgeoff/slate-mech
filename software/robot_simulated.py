import compat
from brain import robot
from interfaces.telemetry.udp_sender import TelemetrySender
from interfaces.remote_control.udp_reciever import RemoteControlReciever
from interfaces.chassis.abstract import Chassis as Chassis
import sys

# ---------------- Create the components of the robot -------------------------
telemetry = TelemetrySender(45678)

# Send system information
telemetry.log(telemetry.INFO, "Robot Booting")
if compat.micro:
	telemetry.log(telemetry.INFO, "Running from Micropython")
else:
	telemetry.log(telemetry.INFO, "Running from Cpython")
telemetry.log(telemetry.INFO, "Running on {}".format(sys.platform))


control = RemoteControlReciever(telemetry, 45679)
chassis = Chassis()


main_robot = robot.Robot(
	telemetry,
	control,
	chassis
)


# -------------------------------- Main Loop ---------------------------------
while(1):
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

