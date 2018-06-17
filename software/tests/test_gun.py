"""tests the safeties of the gun"""
import fixpath
from brain.gun import Gun
from interfaces.telemetry.abstract import TelemetrySenderAbstract
from interfaces.chassis.abstract import Chassis
import pytest

from unittest.mock import Mock



def count_shots(chassis):
    count = 0
    for call in chassis.set_digital.call_args_list:
        if call[0][0] == chassis.PIN_GUN:
            if bool(call[0][1]) != False:
                count += 1
    return count


def test_no_shoot_on_init():
    chassis = Mock()
    gun = Gun(TelemetrySenderAbstract(), chassis)
    gun.update()
    gun.update()
    gun.update()
    gun.update()
    gun.update()

    assert count_shots(chassis) == 0



def test_no_shoot_on_inactive():
    chassis = Mock()
    gun = Gun(TelemetrySenderAbstract(), chassis)
    gun.update()
    gun.active = False
    gun.update()
    gun.set_id(1)
    gun.update()
    gun.set_id(2)
    gun.update()
    gun.update()

    assert count_shots(chassis) == 0


def test_no_shoot_when_activating():
    chassis = Mock()
    gun = Gun(TelemetrySenderAbstract(), chassis)
    gun.update()
    gun.active = False
    gun.update()
    gun.set_id(1)
    gun.update()
    gun.set_id(2)
    gun.update()
    gun.active = True
    gun.update()
    gun.update()
    gun.update()

    assert count_shots(chassis) == 0


def test_shoot_when_active():
    chassis = Mock()
    gun = Gun(TelemetrySenderAbstract(), chassis)
    gun.update()
    gun.active = True
    gun.update()
    gun.set_id(1)
    gun.update()
    gun.set_id(2)
    gun.update()
    gun.update()

    assert count_shots(chassis) == 2



if __name__ == "__main__":
    pytest.main()
