from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)
from .log import logger

from time import sleep
from threading import Lock

import gpiozero.pins.data
from gpiozero.pins.mock import MockPin

from picraftzero.config import get_config
from picraftzero.version import build_string

logger.info("picraftzero, version={}".format(build_string))

try:
    pi_info = gpiozero.pins.data.pi_info()
    logger.debug("Pi info is {}".format(pi_info))
    RUNNING_ON_PI = True
except (FileNotFoundError, gpiozero.exc.PinUnknownPi):
    RUNNING_ON_PI = False

if not RUNNING_ON_PI:
    logger.info("Not running on a Pi, using MockPin".format())
    gpiozero.devices.pin_factory = MockPin


logger.info("Selected pin factory is {}".format(gpiozero.devices.pin_factory))

from gpiozero.mixins import SourceMixin,SharedMixin
from gpiozero.devices import Device, CompositeDevice


from .servers import HTTPServer, WebSocketServer as WSS
from .utils import arduino_map, main_loop, exit_main
from .inputs.joystick import InputController
from .providers import get_motor_provider, get_servo_provider


#formatter = logging.Formatter(LOG_FORMAT)
#rotating_log_handler = TimedRotatingFileHandler('picraftzero.log',
#                                   when="d",
#                                   interval=1,
#                                   backupCount=7)
#rotating_log_handler.setFormatter(formatter)
#rotating_log_handler.setLevel(log_level)

#logger.addHandler(rotating_log_handler)



# ----------------------
# Websocket

# TODO: some fixing in this...
class MessageReceiver(SharedMixin, Device):
    def __init__(self, port=8001, **args):
        self._port = port
        self._last_event_type = None
        self._last_event_data = None
        self._last_event_id = None
        self._last_message = {}
        self._listeners = []

        self._http_server = HTTPServer() # TODO: accept port param
        self._ws_server = WSS(self, ws_port=port)
        self._http_server.start()
        self._ws_server.start()
        super(MessageReceiver, self).__init__(**args)

    @classmethod
    def _shared_key(cls, port):
        return None             # always returning same value means only ever a single instance is created

    def on_websocket_message(self, message):
        logger.debug("on_websocket_message: {}".format(message))
        self._last_message = message
        self.dispatch_listener_message(message)

    def add_listener(self, func):
        self._listeners.append(func)

    def remove_listener(self, func):
        self._listeners.remove(func)

    def dispatch_listener_message(self, message):
        for listener in self._listeners:
            listener(message)


    @property
    def port(self):
        return self._port

    def _read(self):
        # if self._last_message:
        #     msg = self._last_message.copy()
        #     self._last_message = None
        # else:
        #     msg = None
        # return msg
        return self._last_message



    @property
    def value(self):
        return self.raw_value

    @property
    def raw_value(self):
        """
        The raw value as read from the device.
        """
        return self._read()

    def stop(self):
        self._http_server.stop()
        self._ws_server.stop()



class Joystick(Device, SourceMixin):

    def __init__(self, joystick_id=0, **args):
        super(Joystick, self).__init__(**args)

        self._value = (0, 0)
        self.joystick_id = joystick_id
        self.joystick = InputController(self.joystick_id)
        self.joystick.add_listener(self.joystick_event)

        self._x_axis_name = None
        self._y_axis_name = None

        config = get_config()
        config_section = 'joystick_{}'.format(self.joystick_id)
        self.ws_port = config.getint('www', 'ws_port', fallback=8001)
        self.invert_x_axis = config.getboolean(config_section, 'invert_x_axis', fallback=False)
        self.invert_y_axis = config.getboolean(config_section, 'invert_y_axis', fallback=False)

        self.messages = MessageReceiver(self.ws_port)           # a 'shared' (singleton) resource
        self.messages.add_listener(self.message_recv)

        if joystick_id == 1:
            self._x_axis_name, self._y_axis_name = ('lx', 'ly')
        else:
            self._x_axis_name, self._y_axis_name = ('rx', 'ry')

        logger.info(self)


    def __str__(self):
        return "Joystick(id={}, xname={}, yname={}, xinvert={}, yinvert={}".format(self.joystick_id, self._x_axis_name, self._y_axis_name, self.invert_x_axis, self.invert_y_axis)

    def close(self):
        super(Joystick, self).close()
        self.messages.stop()

    def message_recv(self, message):
        if message["type"] == "JOYSTICK" and message["id"] == self.joystick_id:
            self._value = tuple(message['data'])
            logger.debug("message_recv: value = {}".format(self._value))

    def joystick_event(self, joystick):
        x_axis = int(joystick.get_value(self._x_axis_name))
        y_axis = int(joystick.get_value(self._y_axis_name))
        x_axis = -x_axis if self.invert_x_axis else x_axis
        y_axis = -y_axis if self.invert_y_axis else y_axis
        self._value = (x_axis, y_axis)

        logger.debug("joystick_event: value = {}".format(self._value))

    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, value):
        self._value = value


# ----------------------
# OUtput device


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
        logger.debug("Wheelbase.value={}".format(value))
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

# Debugging Helper

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



# *Zero 'Source' utilities

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



from .utils import differential_steering
def steering_mixer(values, axis_max=100):
    it = iter(values)
    while True:
        (yaw, throttle) = next(it)
        yield differential_steering(-yaw, throttle, axis_max)


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


def custom_source_tool(func, values):
    it = iter(values)
    while True:
        yield func(*next(it))


# Misc

from picraftzero.servers import CameraServer


def start():
    config = get_config()
    # TODO: perhaps be more explicit and not rely on this convention of 'ws'
    if config['hmd']['camera_mono_url'].lower().startswith('ws'):
        cs = CameraServer()
        cs.start()
    main_loop()


def stop():
    logger.info("Stopping picraftzero")
    exit_main()