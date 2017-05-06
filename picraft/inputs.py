import threading
import logging
logger = logging.getLogger(__name__)

from .utils import arduino_map

USE_EVENT=False
USE_PYGAME=False

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

if USE_EVENT:
    logger.info("InputController using Event implementation")

    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'ABS_X', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'ly': {'event_name': 'ABS_Y', 'mapfunc': lambda x: arduino_map(x, 0, 255, 100, -100)},
        'rx': {'event_name': 'ABS_Z', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'ry': {'event_name': 'ABS_RZ', 'mapfunc': lambda x: arduino_map(x, 0, 255, 100, -100)},
    }

    VENDOR_PRODUCT_MAPPINGS = {
        "3695:296": ROCKCANDY_MAPPING,
    }


    class InputController:


        def __init__(self, controller_id=0):

            # TODO: bounds checking and exception handling
            devices = list_devices()
            device_path = devices[controller_id]

            self.input_device = InputDevice(device_path)
            self.controller_state = {}
            self.keep_running = True
            self.thread = threading.Thread(target=self._start)
            self.thread.daemon = True
            self.thread.start()

            vpid = "{}:{}".format(self.input_device.info.vendor, self.input_device.info.product)
            self.mapping = VENDOR_PRODUCT_MAPPINGS[vpid]

        def _start(self):
            for event in self.input_device.read_loop():
                cat_event = categorize(event)
                if isinstance(cat_event, AbsEvent):
                    self.controller_state[ABS[cat_event.event.code]] = event.value
                if not self.keep_running:
                    break

        def stop(self):
            self.keep_running = False

        def get_value(self, name):
            value = 0
            if name in self.mapping:
                event_info = self.mapping[name]
                event_name = event_info['event_name']
                if event_name in self.controller_state:
                    mapfunc = event_info['mapfunc']
                    value = mapfunc(self.controller_state[event_name])

            return value

elif USE_PYGAME:
    from time import sleep
    from .utils import mainthread_dispatch

    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x*100)},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x*-100)},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x*100)},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x*-100)},
    }

    JOYSTICK_NAME_MAPPINGS = {
        "Rock Candy Wireless Gamepad for PS3": ROCKCANDY_MAPPING,
    }


    #skip this until pygame is replaced or: http://stackoverflow.com/questions/18989446/execute-python-function-in-main-thread-from-call-in-dummy-thread
    logger.info("InputController using PyGame implementation")
    pygame.init()

    count = pygame.joystick.get_count()
    joystick_names = []
    for i in range(0, count):
        joystick_names.append(pygame.joystick.Joystick(i).get_name())

    logger.info("Joysticks count {} : {}".format(count, joystick_names))


    class InputController:

        def __init__(self, controller_id=0):
            self.controller_state = {}
            self.mapping = {}
            self.keep_running = True


            try:
                self.joystick = pygame.joystick.Joystick(controller_id)
                self.joystick.init()
                self.thread = threading.Thread(target=self._start)
                self.thread.daemon = True
                self.thread.start()
                self.joystick_name = self.joystick.get_name()
                self.joystick_num_axes = self.joystick.get_numaxes()
                logger.info("Enabled joystick: {}".format(self.joystick_name))
                logger.info("Joystick info:  Axes={}".format(self.joystick_num_axes))

                self.mapping = JOYSTICK_NAME_MAPPINGS[self.joystick_name]

            except pygame.error:
                logger.warning("No joystick found.")


        def stop(self):
            self.keep_running = False


        def _start(self):
            while self.keep_running:
                mainthread_dispatch(lambda: self._process_events(pygame.event.get()))
                sleep(0.01)

        def _process_events(self, events):
            # TODO: to place nicely with other toys in the future this really should be fed from a global event loop
            for e in events:
                if e.type == JOYAXISMOTION:
                    for axis_num in range(0, self.joystick_num_axes):
                        self.controller_state['AXIS'+str(axis_num)] = self.joystick.get_axis(axis_num)

        def get_value(self, name):
            value = 0
            if name in self.mapping:
                event_info = self.mapping[name]
                event_name = event_info['event_name']
                if event_name in self.controller_state:
                    mapfunc = event_info['mapfunc']
                    value = mapfunc(self.controller_state[event_name])
            return value

else:

    class InputController:

        def __init__(self, controller_id=0):
            pass

        def stop(self):
            pass

        def get_value(self, name):
            return 0