import threading
from evdev import InputDevice, categorize, AbsEvent, list_devices
from evdev.ecodes import KEY, SYN, REL, ABS
from .utils import arduino_map

class InputController:
    ROCKCANDY_MAPPING = {
        'lx': {'event_name': 'ABS_X', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'ly': {'event_name': 'ABS_Y', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'rx': {'event_name': 'ABS_Z', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
        'ry': {'event_name': 'ABS_RZ', 'mapfunc': lambda x: arduino_map(x, 0, 255, -100, 100)},
    }

    VENDOR_PRODUCT_MAPPINGS = {
        "3695:296": ROCKCANDY_MAPPING,
    }

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
        self.mapping = InputController.VENDOR_PRODUCT_MAPPINGS[vpid]

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
