# ----------------
import logging
import threading
import platform
from time import sleep

logger = logging.getLogger(__name__)


ON_MAC = False
ON_WINDOWS = False
ON_LINUX = False
_platform = platform.system().lower()
if _platform.startswith("linux"):
    ON_LINUX = True
    logger.debug("Running on Linux ({})".format(_platform))
    from picraft.thirdparty.inputs import get_gamepad, get_key, get_mouse, devices
elif _platform.startswith("darwin"):
    ON_MAC = True
    logger.debug("Running on Mac ({})".format(_platform))

elif _platform.startswith("win32"):
    ON_WINDOWS = True
    logger.debug("Running on Windows ({})".format(_platform))
else:
    raise Exception("Unsupported platform '{}'".format(platform.system()))


if ON_MAC:
    import pygame
    pygame.init()
    class DeviceManager(object):
        def __init__(self):
            self.gamepads = []

    devices = DeviceManager()

    def get_gamepad():
        return []

    def get_mouse():
        return []

    def get_key():
        pygame.event.pump()  # Need to call the event queue for the program to not lock up.
        key = pygame.key.get_pressed()
        #if key[pygame.K_a]:
        #    logger.debug("You pressed 'a'")
        if key[pygame.K_ESCAPE]:  # Press 'q' to exit the program
            raise SystemExit
        return pygame.event.get()


class InputHandler:

    def __init__(self, keyboard_handler=None, mouse_handler=None, joypad_handler=None):
        self.keep_running = True
        self.keyboard_handler = keyboard_handler
        self.mouse_handler = mouse_handler
        self.joypad_handler = joypad_handler
        logger.debug("Input devices = {}".format(devices))
        self.joypad_fatal_raised=False

    def poll(self):
        if self.joypad_handler:
            try:
                events = get_gamepad()
                for event in events:
                    if self.joypad_handler:
                        self.joypad_handler(event)
            except OSError:
                if not self.joypad_fatal_raised:
                    logger.exception("Fatal error, the Joypad event read failed, has it disconnected since startup? ")
                self.joypad_fatal_raised = True

        if self.keyboard_handler:
            events = get_key()
            for event in events:
                if self.keyboard_handler:
                    self.keyboard_handler(event)

        if self.mouse_handler:
            events = get_mouse()
            for event in events:
                if self.mouse_handler:
                    self.mouse_handler(event)
                    #print(event.ev_type, event.code, event.state)


    def _start(self):
        while self.keep_running:
            self.poll()
            sleep(0.05)

    def start(self, use_threads = False):
        if not len(devices.gamepads) > 0:
            logger.warning("No joypads found")
            self.joypad_handler = None

        try:
            if not len(devices.keyboards) > 0:
                logger.warning("No keyboards found")
                self.keyboard_handler = None
        except AttributeError:
            logger.error("Input library is missing keyboards, running on a Mac?")



        try:
            if not len(devices.mice) > 0:
                logger.warning("No mice found")
                self.mouse_handler = None
        except AttributeError:
            logger.error("Input library is missing mice, running on a Mac?")

        if use_threads:
            self.update_thread = threading.Thread(target=self._start, name = __class__)
            self.update_thread.daemon = False
            self.update_thread.start()
        else:
            logger.info("inputs not using threds")

    def stop(self):
        self.keep_running = False