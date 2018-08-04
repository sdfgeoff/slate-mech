import gc
import uos
from flashbdev import bdev

try:
    if bdev:
        uos.mount(bdev, '/')
except OSError:
    import inisetup
    vfs = inisetup.setup()


try:
    uos.stat('/main.py')
except OSError:
    with open("/main.py", "w") as f:
        f.write("""\
import main_robot
""")

gc.collect()

