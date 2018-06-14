import compat
from brain import robot
from interfaces.telemetry.udp_sender import TelemetrySender
from interfaces.remote_control.udp_sender import RemoteControlSender
from interfaces.chassis import abstract as chassis
import sys

# ---------------- Create the components of the robot -------------------------
telemetry = TelemetrySender(45678)

# Send system information
telemetry.send_log_message(telemetry.LOG_INFO, "Robot Booting")
if compat.micro:
	telemetry.send_log_message(telemetry.LOG_INFO, "Running from Micropython")
else:
	telemetry.send_log_message(telemetry.LOG_INFO, "Running from Cpython")
telemetry.send_log_message(telemetry.LOG_INFO, "Running on {}".format(sys.platform))


control = RemoteControlSender(telemetry, 45679)
chassis = None


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
		telemetry.send_log_message(telemetry.LOG_ERROR, repr(error_string))

		# Hope the problem resolves itself....
		compat.time.sleep(0.1)

