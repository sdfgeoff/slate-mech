""" Should be written as an accelerated C module. Contains functions
for doing the geometric manipulations needed for walking """
import math

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vec2({}, {})".format(self.x, self.y)

    def __add__(self, vec):
        self.x += vec.x
        self.y += vec.y


class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, vec):
        return Vec3(
			self.x + vec.x,
			self.y + vec.y,
			self.z + vec.z
		)

    def __repr__(self):
        return "Vec3({}, {}, {})".format(self.x, self.y, self.z)


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
