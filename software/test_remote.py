from interfaces.remote_control.udp_sender import RemoteControlSender
import time

remote = RemoteControlSender(('0.0.0.0', 45679))


while(1):
    time.sleep(0.016)
    if time.time() % 1.0 < 0.1:
        remote.fire()
    remote.update()
    print(remote.packet.bullet_id)
