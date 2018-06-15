"""Used to send data back to the operator"""

class TelemetrySenderAbstract:
    CRITICAL = 4
    ERROR = 3
    WARN = 2
    INFO = 1
    DEBUG = 0



    def log(self, log_level, string):
        """Sends a textual message to the base-station"""
        print(string)

    def var_val(self, varname, val, status=None):
        print("({}) {}:{}".format(varname, val, status))

    def update(self):
        pass
