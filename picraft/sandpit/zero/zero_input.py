from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )

from signal import pause
from threading import Lock

import gpiozero.devices
from gpiozero.pins.mock import MockPin
from gpiozero.mixins import SourceMixin
from gpiozero.devices import GPIODevice, Device, CompositeDevice

from gpiozero.exc import DeviceClosed
from gpiozero.tools import cos_values, scaled, inverted, smoothed

gpiozero.devices.pin_factory = MockPin



# ----------------------
# Input device

class Joystick(Device):
    def __init__(self, joystick_id=0, **args):
        self._joystick_id = joystick_id
        super(Joystick, self).__init__(**args)

    @property
    def joystick_id(self):
        return self._joystick_id

    def _read(self):
        return (123, 789)

    def _send(self):
        return 456

    @property
    def value(self):
        return self.raw_value

    @property
    def raw_value(self):
        """
        The raw value as read from the device.
        """
        return self._read()

# ----------------------
# OUtput device

class CustomOutputDevice(SourceMixin, GPIODevice):
    def __init__(self, id=None):
        super(CustomOutputDevice, self).__init__(id)
        self._lock = Lock()
        self._id = id
        self._state = None

    def _value_to_state(self, value):
        print("_value_to_state: {}".format(value))
        return value

    def _write(self, value):
        try:
            self._state = self._value_to_state(value)
        except AttributeError:
            self._check_open()
            raise

    def on(self):
        self._write(True)

    def off(self):
        self._write(False)

    def toggle(self):
        with self._lock:
            if self.is_active:
                self.off()
            else:
                self.on()

    @property
    def value(self):
        return super(CustomOutputDevice, self).value

    @value.setter
    def value(self, value):
        self._write(value)


# websocket server


out = CustomOutputDevice(4)
joystick = Joystick(1)

out.source = joystick.values
#out.source = scaled(cos_values(100), 0, 1, -1, 1)

#for value in joystick.values:
#for value in smoothed(cos_values(100), 5):
#    print(value)

pause()
