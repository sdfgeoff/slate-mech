from .gun import Gun
from utils import geom
from utils.compat import time
import math


class Robot:
    def __init__(self, telemetry, controller, hardware):
        self.telemetry = telemetry
        self.controller = controller
        self.hardware = hardware

        self.gun = Gun(self.telemetry, self.hardware)
        self._enable_servos(True)

        # Allow the gun to not fire when a controller connects
        self.controller.on_controller_connected.append(
            self._on_controller_connected
        )

        self.walker = TestWalk(self.telemetry, self.hardware)

    def _enable_servos(self, val):
        for servo_id in self.hardware.servo_ids:
            self.hardware.set_servo_param(servo_id, self.hardware.SERVO_ENABLE, val)


    def update(self):
        self.telemetry.update()
        self.controller.update()

        if self.controller.is_connected():
            self.gun.set_id(self.controller.get_bullet_id())
            self.gun.active = self.controller.get_weapon_active()
        else:
            # Powerdown state, stop moving
            self.gun.active = False

        self.walker.update()
        self.gun.update()
        self.hardware.update()

    def _on_controller_connected(self):
        # Ensure the gun won't discharge accidentally by ensuring the ID's
        # line up
        self.gun.sync(self.controller.get_bullet_id())



class Leg:
    def __init__(self, telemetry, hardware, shoulder, elbow, wrist, flipx, flipy, flipangles):
        self.telemetry = telemetry
        self.hardware = hardware
        self.shoulder = shoulder
        self.elbow = elbow
        self.wrist = wrist
        self.flipx = -1 if flipx else 1
        self.flipy = -1 if flipy else 1
        self.flipangles = -1 if flipangles else 1

        self.rest_pos = geom.Vec3(0.07, 0.0, -0.055)

    def get_position(self):
        """Returns a vec3 of the leg position"""
        pos = fk(
            self.hardware.get_servo_param(self.shoulder, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.elbow, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.wrist, self.hardware.SERVO_GET_POSITION),
        )
        #pos.y *= self.flipy
        return pos

    def set_position(self, position):
        position.y *= self.flipy
        position.x *= self.flipx

        position = position + self.rest_pos

        angles = ik(position, self.flipangles)
        self.hardware.set_servo_param(self.shoulder, self.hardware.SERVO_SET_POSITION, angles[0]),
        self.hardware.set_servo_param(self.elbow, self.hardware.SERVO_SET_POSITION, angles[1]),
        self.hardware.set_servo_param(self.wrist, self.hardware.SERVO_SET_POSITION, angles[2]),



class TestWalk:
    def __init__(self, telemetry, hardware):
        self.telemetry = telemetry
        self.hardware = hardware

        self.front_left_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_FRONT_LEFT_SHOULDER,
            self.hardware.LEG_FRONT_LEFT_ELBOW,
            self.hardware.LEG_FRONT_LEFT_WRIST,
            False, True, False
        )
        self.front_right_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_FRONT_RIGHT_SHOULDER,
            self.hardware.LEG_FRONT_RIGHT_ELBOW,
            self.hardware.LEG_FRONT_RIGHT_WRIST,
            True, False, True
        )
        self.back_left_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_BACK_LEFT_SHOULDER,
            self.hardware.LEG_BACK_LEFT_ELBOW,
            self.hardware.LEG_BACK_LEFT_WRIST,
            False, True, True
        )
        self.back_right_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_BACK_RIGHT_SHOULDER,
            self.hardware.LEG_BACK_RIGHT_ELBOW,
            self.hardware.LEG_BACK_RIGHT_WRIST,
            True, False, False
        )

        self.legs = (
            self.front_right_leg,
            self.back_right_leg,
            self.front_left_leg,
            self.back_left_leg,

        )

        self.counter = 0
        self.leg_counter = 0

    def update(self):
        CYCLE_LENGTH = 60
        QUARTER = int(CYCLE_LENGTH/4)
        pos_list = [l.get_position() for l in self.legs]
        for leg_id, leg in enumerate(self.legs):
            raw_percent = self.counter / CYCLE_LENGTH
            percent = raw_percent + (leg_id/4)+1/8
            percent = 1.0 - (percent % 1)

            pos = leg.get_position()
            pos.x = math.sin(raw_percent * 3.14 * 2) * 0.01   #0.0# 2 * math.sin(time.time())
            pos.y = percent * 0.1 - 0.05
            if percent > 0.875 or percent < 0.125:
                pos.z = 0.02
            else:
                pos.z = 0
            #pos.z = 0.001 * math.sin(time.time())+0.001 #-0.055# if leg_id != self.leg_counter else -0.045

            leg.set_position(pos)

        self.counter += 1
        if self.counter % QUARTER == 0:
            self.leg_counter = (self.leg_counter + 1) % 4
        elif self.counter == CYCLE_LENGTH:
            self.counter = 0





L1 = 0.05
L2 = 0.05
L3 = 0.055

def clamp(num, mi=-1, ma=1):
    return max(min(num, ma), mi)

def ik(pos, flipangles):
    """Pass in a Vec3 target position, and get back a tuple of joint angles.
    Position is relative to the legs mounting point"""
    # TODO: Write unit tests
    theta3 = -math.acos(clamp(-pos.z/L3))
    extension = L2 + L3*math.sin(-theta3)
    dist = math.sqrt(pos.x**2 + pos.y **2)
    b1 = math.atan2(pos.y, pos.x)

    a1 = math.acos(clamp((extension**2 + L1**2 - dist**2)/(2 * L1 * extension)))
    a2 = math.acos(clamp((dist**2 + L1**2 - extension**2)/(2 * L1 * dist)))


    theta2 = flipangles * (math.pi - a1)
    theta1 = b1 - a2 * flipangles
    return (theta1, theta2, theta3)



def fk(theta1, theta2, theta3):
    """Pass in the joint angles and get back a Vec3 of the foot position
    Position is relative to the legs mounting point"""
    # TODO: Write unit tests
    extension = L2 + L3*math.sin(-theta3)
    x = L1 * math.cos(theta1) + extension * math.cos(theta1 - theta2)
    y = L1 * math.sin(theta1) + extension * math.sin(theta1 - theta2)
    z = -L3 * math.cos(theta3)
    return geom.Vec3(x, y, z)
