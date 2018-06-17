"""Used to send data back to the operator"""

class TelemetrySenderAbstract:
    # Message statusus
    CRITICAL = 4
    ERROR = 3
    WARN = 2
    INFO = 1
    DEBUG = 0

    def log(self, log_level, string):
        """Sends a textual message to the base-station. Probably to tell the
        user why the robot failed"""
        print(string)

    def var_val(self, varname, val, status=None):
        """Transmit a variable:value pair. The optional status allows
        the reciving program to know if the value is in an acceptable range
        or not"""
        print("({}) {}:{}".format(varname, val, status))

    def update(self):
        pass
