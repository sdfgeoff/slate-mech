from .gun import Gun
from utils import geom
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



class TestWalk:
    def __init__(self, telemetry, hardware):
        self.telemetry = telemetry
        self.hardware = hardware

        self.leg_counter = 0
        self.counter = 0

    def _get_leg_positions(self):
        fl_leg_pos = fk(
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_LEFT_SHOULDER, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_LEFT_ELBOW, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_LEFT_WRIST, self.hardware.SERVO_GET_POSITION),
        )
        fr_leg_pos = fk(
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_RIGHT_SHOULDER, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_RIGHT_ELBOW, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_FRONT_RIGHT_WRIST, self.hardware.SERVO_GET_POSITION),
        )
        bl_leg_pos = fk(
            self.hardware.get_servo_param(self.hardware.LEG_BACK_LEFT_SHOULDER, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_BACK_LEFT_ELBOW, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_BACK_LEFT_WRIST, self.hardware.SERVO_GET_POSITION),
        )
        br_leg_pos = fk(
            self.hardware.get_servo_param(self.hardware.LEG_BACK_RIGHT_SHOULDER, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_BACK_RIGHT_ELBOW, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.hardware.LEG_BACK_RIGHT_WRIST, self.hardware.SERVO_GET_POSITION),
        )
        return (fl_leg_pos, bl_leg_pos, fr_leg_pos, br_leg_pos)

    def _set_leg_positions(self, fl_pos, bl_pos, fr_pos, br_pos):
        angles = ik(fl_pos)
        #print(fl_pos)
        #print(angles)
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_LEFT_SHOULDER, self.hardware.SERVO_SET_POSITION, angles[0]),
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_LEFT_ELBOW, self.hardware.SERVO_SET_POSITION, angles[1]),
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_LEFT_WRIST, self.hardware.SERVO_SET_POSITION, angles[2]),

        angles = ik(fr_pos)
        #print(fr_pos)
        #print(angles)
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_RIGHT_SHOULDER, self.hardware.SERVO_SET_POSITION, angles[0]),
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_RIGHT_ELBOW, self.hardware.SERVO_SET_POSITION, angles[1]),
        self.hardware.set_servo_param(self.hardware.LEG_FRONT_RIGHT_WRIST, self.hardware.SERVO_SET_POSITION, angles[2]),

        angles = ik(bl_pos)
        #print(bl_pos)
        #print(angles)
        self.hardware.set_servo_param(self.hardware.LEG_BACK_LEFT_SHOULDER, self.hardware.SERVO_SET_POSITION, angles[0]),
        self.hardware.set_servo_param(self.hardware.LEG_BACK_LEFT_ELBOW, self.hardware.SERVO_SET_POSITION, angles[1]),
        self.hardware.set_servo_param(self.hardware.LEG_BACK_LEFT_WRIST, self.hardware.SERVO_SET_POSITION, angles[2]),

        angles = ik(br_pos)
        #print(br_pos)
        #print(angles)
        self.hardware.set_servo_param(self.hardware.LEG_BACK_RIGHT_SHOULDER, self.hardware.SERVO_SET_POSITION, angles[0]),
        self.hardware.set_servo_param(self.hardware.LEG_BACK_RIGHT_ELBOW, self.hardware.SERVO_SET_POSITION, angles[1]),
        self.hardware.set_servo_param(self.hardware.LEG_BACK_RIGHT_WRIST, self.hardware.SERVO_SET_POSITION, angles[2]),


    def update(self):
        #if self.counter == 0:
        pos_list = self._get_leg_positions()
        for p_id, pos in enumerate(pos_list):
            pos.x = 0.07
            pos.y = 0.05 - self.counter/5000
            if p_id >= 2:
                pos.y = - pos.y
            pos.z = -0.055
        self._set_leg_positions(*pos_list)
        self.counter += 1




L1 = 0.05
L2 = 0.05
L3 = 0.055

def clamp(num, mi=-1, ma=1):
    return max(min(num, ma), mi)

def ik(pos):
    """Pass in a Vec3 target position, and get back a tuple of joint angles.
    Position is relative to the legs mounting point"""
    # TODO: Write unit tests
    theta3 = math.acos(clamp(-pos.z/L3))
    extension = L2 + L3*math.sin(theta3)
    dist = math.sqrt(pos.x**2 + pos.y **2)
    b1 = math.atan2(pos.y, pos.x)

    a1 = math.acos(clamp((extension**2 + L1**2 - dist**2)/(2 * L1 * extension)))
    a2 = math.acos(clamp((dist**2 + L1**2 - extension**2)/(2 * L1 * dist)))


    theta2 = math.pi - a1
    theta1 = b1 - a2
    return (theta1, theta2, theta3)



def fk(theta1, theta2, theta3):
    """Pass in the joint angles and get back a Vec3 of the foot position
    Position is relative to the legs mounting point"""
    # TODO: Write unit tests
    extension = L2 + L3*math.sin(theta3)
    x = L1 * math.cos(theta1) + extension * math.cos(theta1 - theta2)
    y = L1 * math.sin(theta1) + extension * math.sin(theta1 - theta2)
    z = -L3 * math.cos(theta3)
    return geom.Vec3(x, y, z)
