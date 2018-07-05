from interfaces.chassis import abstract
import math
import bge


class Chassis(abstract.Chassis):
    def __init__(self, root_obj):
        bge.constraints.setNumTimeSubSteps(10)
        self.root_obj = root_obj
        self.all_objs = NamedList(root_obj.childrenRecursive)

        self._servos = {
            self.LEG_FRONT_LEFT_SHOULDER: self._make_servo('FrontLeftShoulder'),
            self.LEG_FRONT_LEFT_ELBOW: self._make_servo('FrontLeftElbow'),
            self.LEG_FRONT_LEFT_WRIST: self._make_servo('FrontLeftWrist'),

            self.LEG_FRONT_RIGHT_SHOULDER: self._make_servo('FrontRightShoulder'),
            self.LEG_FRONT_RIGHT_ELBOW: self._make_servo('FrontRightElbow'),
            self.LEG_FRONT_RIGHT_WRIST: self._make_servo('FrontRightWrist'),

            self.LEG_BACK_LEFT_SHOULDER: self._make_servo('BackLeftShoulder'),
            self.LEG_BACK_LEFT_ELBOW: self._make_servo('BackLeftElbow'),
            self.LEG_BACK_LEFT_WRIST: self._make_servo('BackLeftWrist'),

            self.LEG_BACK_RIGHT_SHOULDER: self._make_servo('BackRightShoulder'),
            self.LEG_BACK_RIGHT_ELBOW: self._make_servo('BackRightElbow'),
            self.LEG_BACK_RIGHT_WRIST: self._make_servo('BackRightWrist'),

            self.TURRET_PAN: self._make_servo('TurretPan'),
            self.TURRET_ELEVATION: self._make_servo('TurretElevation'),
        }

        root_obj.scene.active_camera = root_obj.scene.objects['RobotCamera']

    def _make_servo(self, obj_name):
        obj = self.all_objs[obj_name]
        join_to = obj.parent

        servo = Servo(
            obj,
            join_to,
            0.04, #0.1,  # max torque = 4kg cm. Need to check units here
            math.pi * 2  # two revolutions per second
        )
        obj.removeParent()
        return servo

    def get_imu_data(self):
        """Format to be decided"""
        pass

    def get_servo_param(self, servo_id, param):
        servo = self._servos[servo_id]
        func = {
            self.SERVO_GET_POSITION: servo.get_position,
            self.SERVO_GET_TORQUE: servo.get_torque,
            self.SERVO_GET_TEMPERATURE: servo.get_temperature,
        }[param]
        return func()

    def set_servo_param(self, servo_id, param, value):
        servo = self._servos[servo_id]
        func = {
            self.SERVO_SET_POSITION: servo.set_position,
            self.SERVO_ENABLE: servo.set_enable,
            self.SERVO_LED: servo.set_led,
        }[param]
        return func(value)

    def set_digital(self, pin_id, val):
        pass

    def get_digital(self, pin_id):
        return 0

    def get_analog(self, pin_id):
        return 0


    def update(self):
        for servo_id in self._servos:
            self._servos[servo_id].update()


class NamedList(list):
    def __getitem__(self, var):
        return next(o for o in self if o.name == var)



class Servo:
    INTERTIA = 0.2
    def __init__(self, servo_obj, horn_obj, max_torque, max_speed):
        self.servo_obj = servo_obj
        self.horn_obj = horn_obj
        self.max_torque = max_torque
        self.max_speed = max_speed

        self._prev_vel = 0.0

        self._constraint = bge.constraints.createConstraint(
            self.servo_obj.getPhysicsId(),
            self.horn_obj.getPhysicsId(),
            bge.constraints.GENERIC_6DOF_CONSTRAINT,
            0, 0, 0,
            0, 0, 0,
            128
        )

        angle_range = 2*math.pi - math.pi/6

        self.p_gain = 100

        self._constraint.setParam(0, 0, 0)
        self._constraint.setParam(1, 0, 0)
        self._constraint.setParam(2, 0, 0)
        self._constraint.setParam(3, 0, 0)
        self._constraint.setParam(4, 0, 0)
        self._constraint.setParam(5, -angle_range/2, angle_range/2)

        self._target_angle = 0
        self._applied_torque = 0
        self._enable = False

    def set_position(self, position):
        """Where the servo is homing to in radians"""
        self._target_angle = position

    def set_enable(self, val):
        self._enable = val

    def set_led(self, val):
        pass

    def get_position(self):
        return self._constraint.getParam(5)

    def get_temperature(self):
        return 25

    def get_torque(self):
        return _applied_torque

    def update(self):
        if self._enable:
            current_angle = self._constraint.getParam(5)
            delta = self._target_angle - current_angle
            delta *= self.p_gain

            delta = max(min(delta, self.max_speed), -self.max_speed)
            delta = self._prev_vel * self.INTERTIA + delta * (1 - self.INTERTIA)
            _applied_torque = delta  # Approximately
            self._constraint.setParam(11, delta, self.max_torque)
