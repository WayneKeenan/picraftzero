from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)
from time import sleep
from signal import pause
from threading import Lock
import logging

logger = logging.getLogger(__name__)


import gpiozero.devices
from gpiozero.pins.mock import MockPin
from gpiozero.mixins import SourceMixin, ValuesMixin, SharedMixin
from gpiozero.devices import GPIODevice, Device, CompositeDevice, GPIOBase
from gpiozero import ButtonBoard, AnalogInputDevice, Button
from gpiozero.exc import DeviceClosed
from gpiozero.tools import cos_values, scaled, inverted, smoothed, negated
gpiozero.devices.pin_factory = MockPin      # TODO: only do this on non-PI platforms



from picraft.servers import HTTPServer, WebSocketServer as WSS


from .utils import arduino_map, constrain
# def arduino_map(x, in_min, in_max, out_min, out_max):
#     return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
#
# def constrain(val, min_val, max_val):
#     return min(max_val, max(min_val, val))

# ----------------------
# Input device


class MessageReceiver(SharedMixin, Device):
    def __init__(self, port=8001, **args):
        self._port = port
        self._last_event_type = None
        self._last_event_data = None
        self._last_event_id = None
        self._last_message = {}

        self._http_server = HTTPServer() # TODO: accept port param
        self._ws_server = WSS(self, ws_port=port)
        self._http_server.start()
        self._ws_server.start()
        super(MessageReceiver, self).__init__(**args)

    @classmethod
    def _shared_key(cls, port):
        return None

    def on_websocket_message(self, message):
        logger.debug("on_websocket_message: {}".format(message))
        #message["data"] = tuple(message["data"])
        self._last_message = message


    @property
    def port(self):
        return self._port

    def _read(self):
        # return self._last_event_data
        #if self._last_message:
        #    msg = self._last_message.copy()
        #    self._last_message = (0, 0)
        #else:
        #    msg = None
        #return msg
        return self._last_message

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


try:
    from approxeng.input.selectbinder import bind_controller
    from approxeng.input.controllers import find_controllers


    d = find_controllers()[0]
    controller = d['controller']
    devices = d['devices']
    logger.debug(controller)
    bind_controller(devices, controller)

    class Joystick(Device, SourceMixin):
        def __init__(self, joystick_id=0, **args):
            super(Joystick, self).__init__(**args)

            self._last_x_axis = None
            self._last_y_axis = None

            self.messages = MessageReceiver(8001)
            self.source = filter_messages(self.messages.values, type='JOYSTICK', id=joystick_id)
            self._value = (0, 0)


            if joystick_id == 1:
                x_axis_name, y_axis_name = ('lx', 'ly')

            else:
                x_axis_name, y_axis_name = ('rx', 'ry')

            self._x_axis_name = x_axis_name
            self._y_axis_name = y_axis_name

            # self._joystick = controller

        @property
        def value(self):
            if self._value[0] is not None or self._value[1] is not None:
                return self._value
            (x_axis, y_axis) = controller.get_axis_values(self._x_axis_name, self._y_axis_name)
            return int(x_axis*100), int(y_axis*100)
            # (x_axis, y_axis) = ( int(x_axis*100), int(y_axis*100))
            # if x_axis != self._last_x_axis and y_axis != self._last_y_axis:
            #     self._last_x_axis = x_axis
            #     self._last_y_axis = y_axis
            #     return tuple([x_axis, y_axis])
            # else:
            #     return (None, None)

        @value.setter
        def value(self, value):
            self._value = value

except (ImportError, IndexError):
    logger.warning("Input dependancy (library or joystick) not found, defaulting to stub")
    class Joystick(Device, SourceMixin):
        def __init__(self, joystick_id=0, **args):

            super(Joystick, self).__init__(**args)
            self.messages = MessageReceiver(8001)
            self.source = filter_messages(self.messages.values, type='JOYSTICK', id=joystick_id)
            self._value = (0,0)

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            self._value = value




# ----------------------
# OUtput device


from picraft.providers import get_motor_provider, get_servo_provider


class PiCraftMotor(SourceMixin, Device):
    def __init__(self, _id=0):
        super(PiCraftMotor, self).__init__()
        self._lock = Lock()
        self._id = _id
        self._state = None
        Motor = get_motor_provider()
        self._motor = Motor(_id)

    def _write(self, value):
        try:
            self._state = self._motor.set_speed(value)
        except AttributeError:
            self._check_open()
            raise

    @property
    def value(self):
        return super(PiCraftMotor, self).value

    @value.setter
    def value(self, value):
        self._write(value)


class PiCraftServo(SourceMixin, Device):
    def __init__(self, _id=0):
        super(PiCraftServo, self).__init__()
        self._lock = Lock()
        self._id = _id
        Servo = get_servo_provider()
        self._servo = Servo(_id)

    def _write(self, value):
        try:
            self._servo.set_angle(value)
        except AttributeError:
            # self._check_open()
            raise

    @property
    def value(self):
        return super(PiCraftMotor, self).value

    @value.setter
    def value(self, value):
        self._write(value)


# ---

# ----------
# Composite devices


class Wheelbase(SourceMixin, CompositeDevice):
    def __init__(self, left=None, right=None):
        super(Wheelbase, self).__init__(
            left_motor=PiCraftMotor(left),
            right_motor=PiCraftMotor(right),
            _order=('left_motor', 'right_motor'))

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return super(Wheelbase, self).value

    @value.setter
    def value(self, value):
        self.left_motor.value, self.right_motor.value = value


class PanTilt(SourceMixin, CompositeDevice):
    def __init__(self, pan=None, tilt=None):
        super(PanTilt, self).__init__(
            pan_servo=PiCraftServo(pan),
            tilt_servo=PiCraftServo(tilt),
            _order=('pan_servo', 'tilt_servo'))

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return super(PanTilt, self).value

    @value.setter
    def value(self, value):
        self.pan_servo.value, self.tilt_servo.value = value





def filter_messages(values, type=None, id=None, dedupe=False):
    it = iter(values)
    old_list = None
    while True:
        v = next(it)
        if v and type and v.get('type') == type and v.get('id') == id:
            #print("TYPE:", type)
            data = v.get('data')
            if dedupe:
                if old_list != data:
                    old_list = data.copy()
                    yield tuple(data)
                else:
                    yield None, None
            else:
                yield tuple(data)

        else:
            yield None, None
        sleep(0.01)



def steering_mixer(values, max_power=100):
    it = iter(values)
    while True:
        axis_pair = next(it)
        (yaw, throttle) = axis_pair
        # TODO: change it so that upstream (None, None) pairs are not passed along
        yaw = yaw if yaw else 0
        throttle = throttle if throttle else 0
        left = throttle - yaw
        right = throttle + yaw
        scale = float(max_power) / max(1, abs(left), abs(right))
        yield (int(left * scale), int(right * scale))



def scaled_pair(values, output_min, output_max, input_min=0, input_max=1):
    #print("VALUES:", values)

    it = iter(values)
    while True:
        pair = next(it)
        #print("PAIR: ", pair)
        (v1, v2) = pair
        # TODO: change it so that upstream (None, None) pairs are not passed along
        v1 = v1 if v1 else 0
        v2 = v2 if v2 else 0

        if input_min >= input_max:
            raise ValueError('input_min must be smaller than input_max')
        input_size = input_max - input_min
        output_size = output_max - output_min
        yield int((((v1 - input_min) / input_size) * output_size) + output_min), int((((v2 - input_min) / input_size) * output_size) + output_min)


def scaled_pair_NEW(values, output_min, output_max, input_min=0, input_max=1):
    print("VALUES:", values)
    sentinel = object()

    iterators = [iter(it) for it in values]
    while iterators:
        for it in iterators:
            elem = next(it, sentinel)
            print ("ELEM:", elem)
            if elem is sentinel:
                return
            (v1, v2) = elem
            v1 = v1 if v1 else 0
            v2 = v2 if v2 else 0

            if input_min >= input_max:
                raise ValueError('input_min must be smaller than input_max')
            input_size = input_max - input_min
            output_size = output_max - output_min
            yield (((v1 - input_min) / input_size) * output_size) + output_min, (
            ((v2 - input_min) / input_size) * output_size) + output_min



def pantilt_converter(values):
    it = iter(values)
    while True:
        axis_pair = next(it)
        (pan, tilt) = axis_pair
        pan = pan if pan else 0
        tilt = tilt if tilt else 0
        pan = arduino_map(pan, -100, 100, 0, 180)
        tilt = arduino_map(tilt, -100, 100, 0, 180)
        yield (pan, tilt)

from time import sleep
from gpiozero import SourceMixin, Device
from picraft.zero import Joystick

class SourcePrinter(SourceMixin, Device):
    def __init__(self, name=""):
        self._name = name
        super(SourcePrinter, self).__init__()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name:
            self._name = name



    @property
    def value(self):
        return super(SourcePrinter, self).value

    @value.setter
    def value(self, value):
        if value:
            print("SourcePrinter({}): '{}'".format(self._name, value))

def join_values_oldest(*values):
    #print(values)
    it = iter(zip * (values))
    while True:
        v = next(it)
        yield v
        sleep(0.01)

def join_values_old(*values):
    #print("VALUES:", values)

    for v in zip(*values):
        #print("VAL:", v)
        yield v

def join_values(*values):
    #print("VALUES:", values)
    sentinel = object()

    iterators = [iter(it) for it in values]
    while iterators:
        result = (None, None)
        for it in iterators:
            elem = next(it, sentinel)
            #print ("ELEM:", elem)
            if elem is sentinel:
                return
            if any(elem):
                result = elem
                break
        yield tuple(result)

def show_tuples(*values):
    yield values



def custom_source_tool(func, values):
    it = iter(values)
    while True:
        yield func(*next(it))




# ------------------------------------------------------
# notes...

# TODO: create a message pocessor using a shared mixin (singleton)

