import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'onboard'))

from interfaces.remote_control.udp_sender import RemoteControlSender
import time

remote = RemoteControlSender()


while(1):
    time.sleep(0.016)
    #if time.time() % 1.0 < 0.1:
    remote.packet.weapon_active = True
    remote.fire()
    remote.update()
    print(remote.packet.bullet_id)
