""" The abstraction layer for interfacing to a remote control. This is
used to allow different control methods (eg over a network socket, over a
Xbee, bluetooth, etc.) """
import utils


class RemoteControlRecieverAbstract:
    def __init__(self):
        self.on_controller_connected = utils.FunctionList()
        self.on_controller_disconnected = utils.FunctionList()

    def get_linear_velocity(self):
        """Returns the target linear velocity that the user is requesting
        the bot to do"""
        return utils.geom.Vec2(0, 0)

    def get_rotate_velocity(self):
        """Returns the speed which the robot should rotate at."""
        return 0

    def get_gun_elevation(self):
        """Returns the change in gun elevation."""
        return 0

    def get_weapon_active(self):
        """Returns True if the weapon is allowed to fire"""
        return 0

    def get_bullet_id(self):
        """Returns a number that represents the shot count. This is to prevent
        the same "fire" signal from shooting multiple projectiles. The gun will
        only fire if this is different to the previous value. For non-auto, the
        controller increments it once. For full-auto, it can be a running
        counter as the exact value does not matter"""
        return 0

    def time_since_update(self):
        """Return the time in seconds since a control packet was sucessfully
        received"""
        return 9999999

    def update(self):
        """Updates all the values"""
