import threading
import logging
from .utils import arduino_map

USE_EVENT = False
USE_PYGAME = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------------------

# TODO: other joypads
# TODO: test the PyGame impl. on Windows
# TODO: shared common behaviour refactor

# ---------------------------------------------------------------------------------------------------------
# Look for Event support first (Linux) then PyGame (Linux, Windows, Mac, other)
try:
    from evdev import InputDevice, categorize, AbsEvent, list_devices
    from evdev.ecodes import KEY, SYN, REL, ABS
    USE_EVENT = True
except ImportError:
    try:
        import pygame
        from pygame.locals import *
        USE_PYGAME = True
    except ImportError:
        logger.warning("InputController failing back to stub implementation")



# ---------------------------------------------------------------------------------------------------------
if USE_EVENT:
    logger.info("InputController using Event implementation")

    ROCKCANDY_AXIS_DEADZONE = 5
    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'ABS_X', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'ly': {'event_name': 'ABS_Y', 'mapfunc': lambda x: arduino_map(x, 0, 255, 100, -100)},
        'rx': {'event_name': 'ABS_Z', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100) if abs(x-128)> ROCKCANDY_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'ABS_RZ', 'mapfunc': lambda x: arduino_map(x, 0, 255, 100, -100) if abs(x-128)> ROCKCANDY_AXIS_DEADZONE else 0},
    }

    VENDOR_PRODUCT_MAPPINGS = {
        "3695:296": ROCKCANDY_MAPPING,
    }

    class InputController:

        def __init__(self, joystick_id=0):
            self.controller_state = {}
            self.keep_running = True
            self.mapping = {}
            self._listener = None

            devices = list_devices()
            if not len(devices) > 0:
                return
            device_path = devices[0]    # Just joysticks on the first controller, for now

            self.input_device = InputDevice(device_path)
            self.thread = threading.Thread(target=self._start, name="InputController"+str(joystick_id))
            self.thread.daemon = True
            self.thread.start()

            vpid = "{}:{}".format(self.input_device.info.vendor, self.input_device.info.product)
            self.mapping = VENDOR_PRODUCT_MAPPINGS[vpid]

        def _start(self):
            for event in self.input_device.read_loop():
                cat_event = categorize(event)
                if isinstance(cat_event, AbsEvent):
                    axis_key = ABS[cat_event.event.code]
                    axis_val = event.value
                    # TODO: move to init
                    if axis_key not in self.controller_state:
                        self.controller_state[axis_key] = 0

                    if self.controller_state[axis_key] != axis_val:
                        self.controller_state[axis_key] = axis_val
                        if self._listener:
                            self._listener(self)
                if not self.keep_running:
                    break

        def stop(self):
            self.keep_running = False

        def add_listener(self, func):
            self._listener = func

        def get_value(self, name):
            value = 0
            if name in self.mapping:
                event_info = self.mapping[name]
                event_name = event_info['event_name']
                if event_name in self.controller_state:
                    mapfunc = event_info['mapfunc']
                    value = mapfunc(self.controller_state[event_name])

            return value

# ---------------------------------------------------------------------------------------------------------
elif USE_PYGAME:
    logger.info("InputController using PyGame implementation")

    from time import sleep
    from .utils import mainthread_dispatch

    ROCKCANDY_AXIS_DEADZONE = 0.05

    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x*100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x*-100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x*100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x*-100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
    }

    JOYSTICK_NAME_MAPPINGS = {
        "Rock Candy Wireless Gamepad for PS3": ROCKCANDY_MAPPING,                               # Mac
        "Performance Designed Products Rock Candy Wireless Gamepad for PS3": ROCKCANDY_MAPPING,  # Pi
    }

    try:
        pygame.init()
        joystick_count = pygame.joystick.get_count()
        joystick_names = []
        for i in range(0, joystick_count):
            joystick_names.append(pygame.joystick.Joystick(i).get_name())

        logger.info("Joysticks count {} : {}".format(joystick_count, joystick_names))
        if joystick_count > 0:
            joystick_0 = pygame.joystick.Joystick(0)
            joystick_0.init()
            joystick_0_name = joystick_0.get_name()

    except pygame.error as e:
        logger.error("PyGame error during joystick setup, {}".format(e))


    class InputController:

        def __init__(self, joystick_id=0):
            self.keep_running = True
            self.controller_state = {}
            self._listener = None

            if joystick_count < 1 or not (joystick_0_name in JOYSTICK_NAME_MAPPINGS):
                return
            self.joystick = joystick_0
            self.mapping = JOYSTICK_NAME_MAPPINGS[joystick_0_name]

            self.thread = threading.Thread(target=self._start, name="InputController"+str(joystick_id))
            self.thread.daemon = True
            self.thread.start()

        def stop(self):
            self.keep_running = False


        def _start(self):
            logger.info("Using Joystick : {}".format(self.joystick.get_name()))

            while self.keep_running:
                mainthread_dispatch(lambda: self._process_events(pygame.event.get()))
                sleep(0.01)

        def _process_events(self, events):
            # TODO: to place nicely with other toys in the future this really should be fed from a global event loop
            for e in events:
                logger.debug("Joystick event: {}".format(e))
                if e.type == JOYAXISMOTION:
                    for axis_num in range(0, self.joystick.get_numaxes()):
                        axis_key = 'AXIS'+str(axis_num)
                        axis_val = self.joystick.get_axis(axis_num)
                        if axis_key not in self.controller_state or self.controller_state[axis_key] != axis_val:
                            self.controller_state[axis_key] = axis_val
                            if self._listener:
                                self._listener(self)

        def add_listener(self, func):
            self._listener = func

        def get_value(self, name):
            value = 0
            if name in self.mapping:
                event_info = self.mapping[name]
                event_name = event_info['event_name']
                if event_name in self.controller_state:
                    mapfunc = event_info['mapfunc']
                    value = mapfunc(self.controller_state[event_name])
            return value

# ---------------------------------------------------------------------------------------------------------
else: #Stub

    class InputController:

        def __init__(self, controller_id=0):
            pass

        def stop(self):
            pass

        def get_value(self, name):
            return 0

        def add_listener(self, func):
            pass