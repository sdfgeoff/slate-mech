from interfaces.remote_control.udp_sender import RemoteControlSender

import evdev
import utils

import gi
import logging
gi.require_version('Gtk', '3.0')
gi.require_version('Clutter', '1.0')
from gi.repository import Gtk, Gdk, GLib, Clutter

class Control:
    def __init__(self, builder):
        self.builder = builder
        self.sender = RemoteControlSender()
        self.keyboard = None

        for i in range(50):
            try:
                device = evdev.InputDevice('/dev/input/event{}'.format(i))
                if 'keyboard' in device.name.lower():
                    self.keyboard = Keyboard(device)
            except FileNotFoundError:
                break

        if self.keyboard is None:
            logging.error("Unable to find keyboard?!")




    def update(self):
        self.keyboard.update()

        if self.keyboard.get_key('KEY_ENTER') == self.keyboard.JUST_ACTIVE:
            self.sender.set_weapon_active(not self.sender.get_weapon_active())

        line_vel = utils.geom.Vec2(0, 0)
        if self.keyboard.get_key('KEY_W') == self.keyboard.ACTIVE:
            line_vel.x += 1
        if self.keyboard.get_key('KEY_S') == self.keyboard.ACTIVE:
            line_vel.x -= 1
        if self.keyboard.get_key('KEY_A') == self.keyboard.ACTIVE:
            line_vel.y -= 1
        if self.keyboard.get_key('KEY_D') == self.keyboard.ACTIVE:
            line_vel.y += 1
        self.sender.set_linear_velocity(line_vel)


        ang_vel = 0
        turret_elevation = 0
        if self.keyboard.get_key('KEY_LEFT') == self.keyboard.ACTIVE:
            ang_vel -= 1
        if self.keyboard.get_key('KEY_RIGHT') == self.keyboard.ACTIVE:
            ang_vel += 1
        if self.keyboard.get_key('KEY_UP') == self.keyboard.ACTIVE:
            turret_elevation += 1
        if self.keyboard.get_key('KEY_DOWN') == self.keyboard.ACTIVE:
            turret_elevation -= 1
        self.sender.set_turret_elevation(turret_elevation)
        self.sender.set_angular_velocity(ang_vel)

        if self.keyboard.get_key('KEY_SPACE') == self.keyboard.ACTIVE:
            self.sender.fire()


        self.sender.update()



class Keyboard:
    RELEASED = 0
    JUST_ACTIVE = 1
    ACTIVE = 2
    JUST_RELEASED = 3

    def __init__(self, device):
        self.device = device
        self.events = {}

    def get_key(self, keyname):
        return self.events.get(keyname, self.RELEASED)

    def update(self):
        keys = [k[0] for k in self.device.active_keys(True)]
        for key in keys:
            if key not in self.events:
                self.events[key] = self.RELEASED

            prev_status = self.events[key]
            if prev_status == self.JUST_ACTIVE:
                self.events[key] = self.ACTIVE
            elif prev_status != self.ACTIVE:
                self.events[key] = self.JUST_ACTIVE


        for key in self.events:
            if key not in keys:
                prev_status = self.events[key]
                if prev_status == self.JUST_RELEASED:
                    self.events[key] = self.RELEASED
                elif prev_status != self.RELEASED:
                    self.events[key] = self.JUST_RELEASED


