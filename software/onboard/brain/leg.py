from utils import geom
import math


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
        self.rest_pos = geom.Vec3(0.06, -self.flipangles*0.03, -0.055)

        self._target_position = self.get_position()

    def get_position(self):
        """Returns a vec3 of the leg position"""
        pos = fk(
            self.hardware.get_servo_param(self.shoulder, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.elbow, self.hardware.SERVO_GET_POSITION),
            self.hardware.get_servo_param(self.wrist, self.hardware.SERVO_GET_POSITION),
            self.flipangles
        )

        pos = pos - self.rest_pos
        pos.y *= self.flipy
        pos.x *= self.flipx
        return pos

    def get_target_position(self):
        return self._target_position

    def set_position(self, position):
        self._target_position = position.copy()
        position.y *= self.flipy
        position.x *= self.flipx
        position = position + self.rest_pos

        try:
            angles = ik(position, self.flipangles)
        except Exception as e:
            self.telemetry.log(self.telemetry.ERROR, "Ik Failed: {}".format(e))
        else:
            self.hardware.set_servo_param(self.shoulder, self.hardware.SERVO_SET_POSITION, angles[0]),
            self.hardware.set_servo_param(self.elbow, self.hardware.SERVO_SET_POSITION, angles[1]),
            self.hardware.set_servo_param(self.wrist, self.hardware.SERVO_SET_POSITION, angles[2]),


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



def fk(theta1, theta2, theta3, flipangles):
    """Pass in the joint angles and get back a Vec3 of the foot position
    Position is relative to the legs mounting point"""
    # TODO: Write unit tests
    theta2 = -theta2
    extension = L2 + L3*math.sin(-theta3)
    y = L1 * math.sin(theta1) + extension * math.sin(theta1 - theta2)
    x = L1 * math.cos(theta1) + extension * math.cos(theta1 - theta2)
    z = -L3 * math.cos(theta3)
    return geom.Vec3(x, y, z)
