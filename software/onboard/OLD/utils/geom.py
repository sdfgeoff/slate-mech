""" Should be written as an accelerated C module. Contains functions
for doing the geometric manipulations needed for walking """
import math

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vec2({}, {})".format(self.x, self.y)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

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

    def __sub__(self, vec):
        return Vec3(
            self.x - vec.x,
            self.y - vec.y,
            self.z - vec.z
        )

    def __mul__(self, val):
        return Vec3(
            self.x * val,
            self.y * val,
            self.z * val,
        )

    def copy(self):
        return Vec3(
            self.x,
            self.y,
            self.z
        )

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __repr__(self):
        return "Vec3({}, {}, {})".format(self.x, self.y, self.z)


class Mat2:
    def __init__(self, lists):
        self.data = lists


class Mat3:
    def __init__(self, rows):
        self.rows = rows

    def xform_vec(self, vec):
        """Transforms a vector by this matrix"""
        return Vec3(
            self.rows[0][0]*vec.x + self.rows[0][1]*vec.y + self.rows[0][2]*vec.z,
            self.rows[1][0]*vec.x + self.rows[1][1]*vec.y + self.rows[1][2]*vec.z,
            self.rows[2][0]*vec.x + self.rows[2][1]*vec.y + self.rows[2][2]*vec.z,
        )


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Polygon():
    def __init__(self, points):
        self.points = points
