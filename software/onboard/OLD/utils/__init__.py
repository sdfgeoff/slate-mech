from . import geom
from . import compat

class FunctionList(list):
    def call(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

