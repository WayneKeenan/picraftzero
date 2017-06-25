import os
import threading
from picraftzero.utils import arduino_map
from picraftzero.log import logger
from picraftzero.zero import Button

USE_EVENT = True
USE_PYGAME = True
USE_BLUEDOT = False

HAVE_EVENT = False
HAVE_PYGAME = False
HAVE_BLUEDOT = False


# ---------------------------------------------------------------------------------------------------------

# TODO: other joypads
# TODO: test the PyGame impl. on Windows
# TODO: shared common behaviour refactor

# ---------------------------------------------------------------------------------------------------------
# Look for Event support first (Linux) then PyGame (Linux, Windows, Mac, other)
try:
    from evdev import InputDevice, categorize, AbsEvent, KeyEvent, list_devices
    from evdev.ecodes import KEY, SYN, REL, ABS
    HAVE_EVENT = True
except ImportError:
    logger.info("Optional EventDev library not found")
    HAVE_EVENT = False

try:
    import pygame
    from pygame.locals import *
    HAVE_PYGAME = True
except ImportError:
    logger.info("Optional PyGame library not found")
    HAVE_PYGAME = False


try:
    from bluedot import BlueDot
    HAVE_BLUEDOT = True
except ImportError:
    logger.info("Optional BlueDot library not found")
    HAVE_BLUEDOT = False

# ---------------------------------------------------------------------------------------------------------
if HAVE_BLUEDOT and USE_BLUEDOT:
    logger.info("Using BlueDot implementation")
    logger.warning("Only 1 Joystick axis will be available")


    class InputController:
        def __init__(self, controller_id=0):
            self.bd = BlueDot()

        def stop(self):
            pass

        def get_value(self, name):
            value = 0
            if name == 'rx':
                value =  self.bd.position.x
            elif name == 'ry':
                value = self.bd.position.y

            return value

        def add_listener(self, func):
            self.bd.when_moved = lambda x: func(self)

elif HAVE_EVENT and USE_EVENT:
    logger.info("Using EventDev implementation")

    ROCKCANDY_AXIS_DEADZONE = 5
    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'ABS_X', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100,  100) if abs(x-128) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'ABS_Y', 'mapfunc': lambda x: arduino_map(x, 0, 255,  100, -100) if abs(x-128) > ROCKCANDY_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'ABS_Z', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100,  100) if abs(x-128) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'ABS_RZ','mapfunc': lambda x: arduino_map(x, 0, 255,  100, -100) if abs(x-128) > ROCKCANDY_AXIS_DEADZONE else 0},
        'BTN_A': 0,
        'BTN_B': 1,
        'BTN_C': 2,
        'BTN_X': 3,
    }

    AFTERGLOW_MAPPING = ROCKCANDY_MAPPING

    XB360_AXIS_DEADZONE = 500
    XB360_MAPPING = {
        'lx': {'event_name': 'ABS_X', 'mapfunc': lambda x: arduino_map(x, -32768, 32767, -100,  100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'ABS_Y', 'mapfunc': lambda x: arduino_map(x, -32768, 32767,  100, -100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'ABS_RX','mapfunc': lambda x: arduino_map(x, -32768, 32767, -100,  100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'ABS_RY','mapfunc': lambda x: arduino_map(x, -32768, 32767,  100, -100) if abs(x) > XB360_AXIS_DEADZONE else 0},
    }

    VENDOR_PRODUCT_MAPPINGS = {
        "3695:296": ROCKCANDY_MAPPING,
        "1118:654": XB360_MAPPING,          # Wired XBox360
        "1118:673": XB360_MAPPING,          # Wireless XBox360
        "3695:532": AFTERGLOW_MAPPING,
        "DEFAULT": XB360_MAPPING
    }

    class InputController:

        def __init__(self, joystick_id=0):
            self.controller_state = {}
            self.keep_running = True
            self.mapping = {}
            self._listener = None

            devices = list_devices()
            if not len(devices) > 0:
                logger.info("No input devices found")
                return
            logger.info("Found input devices: {}".format(devices))

            device_path = devices[0]    # Just joysticks on the first controller, for now
            logger.info("Using device: {}".format(device_path))
            self.input_device = InputDevice(device_path)
            self.thread = threading.Thread(target=self._start, name="InputController"+str(joystick_id))
            self.thread.daemon = True
            self.thread.start()

            vpid = "{}:{}".format(self.input_device.info.vendor, self.input_device.info.product)
            logger.info("Device USB VPID: {}".format(vpid))
            if vpid in VENDOR_PRODUCT_MAPPINGS:
                self.mapping = VENDOR_PRODUCT_MAPPINGS[vpid]
            else:
                logger.warning("Input device USB VPID not found for '{}', using default".format(vpid))
                self.mapping = VENDOR_PRODUCT_MAPPINGS["DEFAULT"]

        def _start(self):
            for event in self.input_device.read_loop():
                cat_event = categorize(event)
                if isinstance(cat_event, AbsEvent):
                    #logger.debug("Event= {}  Cat={}".format(event, cat_event))

                    axis_key = ABS[cat_event.event.code]
                    axis_val = event.value
                    # TODO: move to init
                    logger.debug("Joypad event: {} = {}".format(axis_key, axis_val))
                    if axis_key not in self.controller_state:
                        self.controller_state[axis_key] = 0

                    if self.controller_state[axis_key] != axis_val:
                        self.controller_state[axis_key] = axis_val
                        if self._listener:
                            self._listener(self)
                elif isinstance(cat_event, KeyEvent):
                    logger.debug("KeyEvent, keycode={}, scancode={}, keystate={}".format(cat_event.keycode, cat_event.scancode, cat_event.keystate))
                    button_id = self._get_button_id(cat_event.keycode)
                    if button_id is not None:
                        Button(button_id).value = 1 if bool(cat_event.keystate) else 0

                else:
                    logger.debug("{}, {}".format(event, cat_event))


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

        def _get_button_id(self, keycodes):
            if not isinstance(keycodes, list):
                keycodes = [keycodes]
            for keycode in keycodes:
                if keycode in self.mapping:
                    return self.mapping[keycode]

            return None


# ---------------------------------------------------------------------------------------------------------
elif HAVE_PYGAME and USE_PYGAME:
    logger.info("Using PyGame implementation")

    from time import sleep
    from picraftzero.utils import mainthread_dispatch

    ROCKCANDY_AXIS_DEADZONE = 0.05

    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x *  100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x * -100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x *  100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x * -100) if abs(x) > ROCKCANDY_AXIS_DEADZONE else 0},
    }

    NIMBUS_AXIS_DEADZONE = 0.05

    NIMBUS_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x *  100) if abs(x) > NIMBUS_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x * -100) if abs(x) > NIMBUS_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x *  100) if abs(x) > NIMBUS_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x * -100) if abs(x) > NIMBUS_AXIS_DEADZONE else 0},
    }

    PS3_AXIS_DEADZONE = 0.05

    PS3_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x *  100) if abs(x) > PS3_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x * -100) if abs(x) > PS3_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x *  100) if abs(x) > PS3_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x * -100) if abs(x) > PS3_AXIS_DEADZONE else 0},
    }

    XB360_AXIS_DEADZONE = 0.05

    XB360_MAPPING = {
        'lx': {'event_name': 'AXIS0', 'mapfunc': lambda x: int(x *  100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'ly': {'event_name': 'AXIS1', 'mapfunc': lambda x: int(x * -100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'rx': {'event_name': 'AXIS2', 'mapfunc': lambda x: int(x *  100) if abs(x) > XB360_AXIS_DEADZONE else 0},
        'ry': {'event_name': 'AXIS3', 'mapfunc': lambda x: int(x * -100) if abs(x) > XB360_AXIS_DEADZONE else 0},
    }

    JOYSTICK_NAME_MAPPINGS = {
        "Rock Candy Wireless Gamepad for PS3": ROCKCANDY_MAPPING,                               # Mac
        "Performance Designed Products Rock Candy Wireless Gamepad for PS3": ROCKCANDY_MAPPING,  # Pi
        "Nimbus": NIMBUS_MAPPING,
        "PLAYSTATION(R)3 Controller": PS3_MAPPING,
        "Wireless 360 Controller": XB360_MAPPING,
        "Xbox 360 Wired Controller": XB360_MAPPING,         # Mac *1
        "Microsoft X-Box 360 pad": XB360_MAPPING,           # Pi  *1     *1 = same actual controller
    }


    # Make an attempt to setup video in order to get the event sub-system up and running
    # TODO: This assumes always headless, users may not want his
    def _setup_video():
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['x11', 'fbcon', 'directfb', 'svgalib', 'Quartz']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logger.error('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break

        if not found:
            logger.error('No suitable SDL video driver found to start the event subsystem, pygame joysticks may not work.')

    try:
        pygame.init()
        _setup_video()
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
        logger.exception("PyGame error during joystick setup, {}".format(e))


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
            # TODO: to play nicely with other toys in the future this really should be fed from a global event loop
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
                elif e.type == JOYBUTTONDOWN:
                    logger.debug(e.button)
                    Button(e.button).value = 1
                elif e.type == JOYBUTTONUP:
                    logger.debug(e.button)
                    Button(e.button).value = 0
                else:
                    logger.debug(e)

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
    logger.warning("Failing back to stub implementation")

    class InputController:

        def __init__(self, controller_id=0):
            pass

        def stop(self):
            pass

        def get_value(self, name):
            return 0

        def add_listener(self, func):
            pass


