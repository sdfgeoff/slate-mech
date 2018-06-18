"""This file defines the functions used to interface between the "brain"
of the robot and the hardware. It is quite low-level access. It acts as the
separation between the simulator and the real robot allowing them to both
use the same brain.
"""

# --------------------------- Public Constants -------------------------------

class Chassis:
    # Pin Allocations ans servo ID's
    BATTERY_PERCENTAGE = 0

    GUN_TRIGGER = 1
    GUN_WARNING_LIGHT = 2


    LEG_FRONT_LEFT_SHOULDER = 0
    LEG_FRONT_LEFT_ELBOW = 1
    LEG_FRONT_LEFT_WRIST = 2

    LEG_FRONT_RIGHT_SHOULDER = 4
    LEG_FRONT_RIGHT_ELBOW = 5
    LEG_FRONT_RIGHT_WRIST = 6

    LEG_BACK_LEFT_SHOULDER = 8
    LEG_BACK_LEFT_ELBOW = 9
    LEG_BACK_LEFT_WRIST = 10

    LEG_BACK_RIGHT_SHOULDER = 12
    LEG_BACK_RIGHT_ELBOW = 13
    LEG_BACK_RIGHT_WRIST = 14

    TURRET_PAN = 16
    TURRET_ELEVATION = 17

    # Servo commands/API's
    SERVO_SET_POSITION = 0x30
    SERVO_ENABLE = 0x24
    SERVO_LED = 0x25

    SERVO_GET_POSITION = 0x37
    SERVO_GET_TORQUE = 0x41
    SERVO_GET_TEMPERATURE = 0x46

    SERVO_LED_RED = 0x01
    SERVO_LED_GREEN = 0x02
    SERVO_LED_BLUE = 0x04
    SERVO_LED_YELLOW = SERVO_LED_RED + SERVO_LED_GREEN
    SERVO_LED_CYAN = SERVO_LED_GREEN + SERVO_LED_BLUE
    SERVO_LED_PINK = SERVO_LED_RED + SERVO_LED_BLUE
    SERVO_LED_WHITE = SERVO_LED_RED + SERVO_LED_BLUE + SERVO_LED_GREEN



    def get_imu_data(self):
        """Format to be decided"""


    def get_servo_param(self, servo_id, param):
        return 0

    def set_servo_param(self, servo_id, param, value):
        return 0


    # GPIO (eg guns, lasers)
    def set_digital(self, pin_id, val):
        pass

    def get_digital(self, pin_id):
        return 0




    # ADC's (eg range-finders, power monitors)
    def get_analog(self, pin_id):
        return 0


    def update(self):
        pass
