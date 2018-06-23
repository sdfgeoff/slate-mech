import bge
import os
import time
import shutil

STREAM_PATH = "/dev/shm/simulator/stream.png"
TMP_FILENAME = '/dev/shm/simulator/stream{}.png'  # So make writing atomic

def run(cont):
    if 'init' not in cont.owner:
        cont.owner['init'] = True
        shutil.rmtree('/dev/shm/simulator')
    counter = cont.owner.get('counter', 0)
    cont.owner['counter'] = (counter + 1)

    older_filename = TMP_FILENAME.format(counter-3)
    new_filename = TMP_FILENAME.format(counter+1)

    if os.path.exists(older_filename):
        os.remove(older_filename)
    bge.render.makeScreenshot(new_filename)

