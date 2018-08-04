from .gun import Gun
from utils import geom
from utils.compat import time
import math

from .leg import Leg


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

        self.walker = WalkCycle(self.telemetry, self.hardware)

    def _enable_servos(self, val):
        for servo_id in self.hardware.servo_ids:
            self.hardware.set_servo_param(servo_id, self.hardware.SERVO_ENABLE, val)


    def update(self):
        self.telemetry.update()
        self.controller.update()

        if self.controller.is_connected():
            self.gun.set_id(self.controller.get_bullet_id())
            self.gun.active = self.controller.get_weapon_active()

            self.walker.set_motion(
                self.controller.get_linear_velocity(),
                self.controller.get_rotate_velocity()
            )
        else:
            # Powerdown state, stop moving
            self.gun.active = False
            self.walker.set_motion(
                geom.Vec2(0, 0),
                0
            )

        self.walker.update()
        self.gun.update()
        self.hardware.update()

    def _on_controller_connected(self):
        # Ensure the gun won't discharge accidentally by ensuring the ID's
        # line up
        self.gun.sync(self.controller.get_bullet_id())


class WalkCycle:
    def __init__(self, telemetry, hardware):
        self.telemetry = telemetry
        self.hardware = hardware

        self.front_left_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_FRONT_LEFT_SHOULDER,
            self.hardware.LEG_FRONT_LEFT_ELBOW,
            self.hardware.LEG_FRONT_LEFT_WRIST,
            False, True, False,
            geom.Vec3(6.7, -6, 0)
        )
        self.front_right_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_FRONT_RIGHT_SHOULDER,
            self.hardware.LEG_FRONT_RIGHT_ELBOW,
            self.hardware.LEG_FRONT_RIGHT_WRIST,
            True, False, True,
            geom.Vec3(6.7, 6, 0)
        )
        self.back_left_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_BACK_LEFT_SHOULDER,
            self.hardware.LEG_BACK_LEFT_ELBOW,
            self.hardware.LEG_BACK_LEFT_WRIST,
            False, True, True,
            geom.Vec3(-6.7, -6, 0)
        )
        self.back_right_leg = Leg(
            self.telemetry, self.hardware,
            self.hardware.LEG_BACK_RIGHT_SHOULDER,
            self.hardware.LEG_BACK_RIGHT_ELBOW,
            self.hardware.LEG_BACK_RIGHT_WRIST,
            True, False, False,
            geom.Vec3(6.7, 6, 0)
        )

        self.legs = (
            self.front_right_leg,
            self.back_right_leg,
            self.front_left_leg,
            self.back_left_leg,
        )

        self.counter = 0
        self.leg_counter = 0

        self._center_point = geom.Vec3(0, 0, 0)
        self._velocity = 0

        for leg in self.legs:
            leg.set_position(geom.Vec3(0, 0, 0))

    def set_motion(self, direction, rotate):
        l_vel = geom.Vec3(direction.x, direction.y, 0)
        if abs(rotate) > 0.01:
            a_vel = geom.Vec3(0, 0, 1/rotate)
        else:
            a_vel = geom.Vec3(0, 0, 99)  # Walk in a 100m circle
        self._center_point = l_vel.cross(a_vel)
        radius = self._center_point.length()
        if radius:
            self._velocity = geom.Vec3(0, 0, direction.length() / radius + rotate)
        else:
            self._velocity = geom.Vec3(0, 0, rotate)

    def update(self):
        # ~ CYCLE_LENGTH = 60
        # ~ QUARTER = int(CYCLE_LENGTH/4)
        # ~ self.counter += 1
        # ~ if self.counter % QUARTER == 0:
            # ~ self.leg_counter = (self.leg_counter + 1) % 4
        # ~ elif self.counter == CYCLE_LENGTH:
            # ~ self.counter = 0

        for leg_id, leg in enumerate(self.legs):
            r_pos = leg.get_target_position_robot()
            radius = r_pos - self._center_point
            target_velocity = radius.cross(self._velocity)
            #print(target_velocity)
            c_pos = leg.get_target_position()
            c_pos = c_pos + target_velocity * 0.001
            leg.set_position(c_pos)




        # ~ for leg_id, leg in enumerate(self.legs):
            # ~ raw_percent = self.counter / CYCLE_LENGTH

            # ~ pos = leg.get_target_position()
            # ~ if leg_id == self.leg_counter:
                # ~ mod_percent = (self.counter % QUARTER) / QUARTER
                # ~ if mod_percent < 0.5 and pos.z < 0.02:
                    # ~ pos.z += 0.01
                # ~ else:
                    # ~ pos.z -= 0.01

                # ~ if pos.z > 0.01:
                    # ~ pos.x = self._lin_motion.x / 40
                    # ~ pos.y = self._lin_motion.y / 25

            # ~ else:
                # ~ pos.x -= self._lin_motion.x / 800 + math.cos(raw_percent * 3.14 * 2) * 0.003
                # ~ pos.y -= self._lin_motion.y / 400 #- math.sin(raw_percent * 3.14 * 2) * 0.003
                # ~ pos.z = 0.0
            # ~ leg.set_position(pos)

        # ~ pos_list = [l.get_position() for l in self.legs]
        # ~ for leg_id, leg in enumerate(self.legs):
            # ~ raw_percent = self.counter / CYCLE_LENGTH
            # ~ percent = raw_percent + (leg_id/4)+1/8
            # ~ percent = 1.0 - (percent % 1)

            # ~ pos = leg.get_position()
            # ~ pos.x = math.sin(raw_percent * 3.14 * 2) * 0.01   #0.0# 2 * math.sin(time.time())
            # ~ pos.y = percent * 0.1 - 0.05
            # ~ if percent > 0.875 or percent < 0.125:
                # ~ pos.z = 0.02
            # ~ else:
                # ~ pos.z = 0
            # ~ #pos.z = 0.001 * math.sin(time.time())+0.001 #-0.055# if leg_id != self.leg_counter else -0.045

            # ~ leg.set_position(pos)


