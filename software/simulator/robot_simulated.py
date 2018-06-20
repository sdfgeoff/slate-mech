import os
import sys

sys.path.append(os.path.normpath(
    os.path.dirname(os.path.abspath(__file__)) + '../../onboard')
)

from utils import compat
from brain import robot
from interfaces.telemetry.udp_sender import TelemetrySender
from interfaces.remote_control.udp_reciever import RemoteControlReciever
from test_chassis import Chassis


# ---------------- Create the components of the robot -------------------------

def init(cont):
    telemetry = TelemetrySender(45678)

    # Send system information
    telemetry.log(telemetry.INFO, "Robot Booting")
    if compat.micro:
        telemetry.log(telemetry.INFO, "Running from Micropython")
    else:
        telemetry.log(telemetry.INFO, "Running from Cpython")
    telemetry.log(telemetry.INFO, "Running on {}".format(sys.platform))


    control = RemoteControlReciever(telemetry)
    chassis = Chassis(cont.owner)

    cont.owner['telemetry'] = telemetry
    cont.owner['main_robot'] = robot.Robot(
        telemetry,
        control,
        chassis
    )

    cont.script = __name__ + '.run'


# -------------------------------- Main Loop ---------------------------------
def run(cont):
    telemetry = cont.owner['telemetry']
    main_robot = cont.owner['main_robot']
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

