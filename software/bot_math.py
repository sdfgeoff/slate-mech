""" Should be written as an accelerated C module """
import math

class Vec2:
	def __init__(self, x, y):
		self.x = x
		self.y = y


class Vec3:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z


class Mat2:
	def __init__(self, lists):
		self.data = lists


class Mat3:
	def __init__(self, lists):
		self.data = lists


class Line:
	def __init__(self, start, end):
		self.start = start
		self.end = end


class Polygon():
	def __init__(self, points):
		self.points = points
