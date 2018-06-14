""" The abstraction layer for interfacing to a remote control. This is
used to allow different control methods (eg over a network socket, over a
Xbee, bluetooth, etc.) """
import bot_math

class RemoteControlAbstract:
	def get_linear_velocity(self):
		"""Returns the target linear velocity that the user is requesting
		the bot to do"""
		return bot_math.Vec2(0, 0)
		
	def get_rotate_velocity(self):
		"""Returns the speed which the robot should rotate at."""
		return 0
		
	def get_gun_elevation(self):
		"""Returns the change in gun elevation."""
		return 0
		
	def get_gun_bullet_id(self):
		"""Returns a number that represents the shot count. This is to prevent
		the same "fire" signal from shooting multiple projectiles. The gun will
		only fire if this is different to the previous value. For non-auto, the
		controller increments it once. For full-auto, it can be a running
		counter as the exact value does not matter"""
		return 0

	def time_since_update(self):
		"""Return the time in seconds since a control packet was sucessfully
		received"""


	def update(self):
		"""Updates all the values"""
