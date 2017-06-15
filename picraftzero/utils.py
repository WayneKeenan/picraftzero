import threading
from time import time, sleep

from picraftzero.log import logger


# see: http://code.activestate.com/lists/python-tutor/96452/
def arduino_map(x, in_min, in_max, out_min, out_max):
    """Return x mapped from in range to out range.

    >>> arduino_map(0, 0, 10, 100, 1000)
    100
    >>> arduino_map(5, 0, 10, 100, 1000)
    550
    >>> arduino_map(10, 0, 10, 100, 1000)
    1000
    
    >>> arduino_map(0, 10, 0, 100, 1000)
    1000
    >>> arduino_map(5, 10, 0, 100, 1000)
    550
    >>> arduino_map(10, 10, 0, 100, 1000)
    100

    >>> arduino_map(0, 0, 10, 1000, 100)
    1000
    >>> arduino_map(10, 0, 10, 1000, 100)
    100

    >>> arduino_map(0, -10, 10, -100, 100)
    0
    >>> arduino_map(128, 0, 255, -100, 100)
    0
    >>> arduino_map(128, 255, 0, 100, -100)
    0
    >>> arduino_map(255, 255, 0, 100, -100)
    100
    >>> arduino_map(0, 255, 0, 100, -100)
    -100

    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min



# see: https://wiki.python.org/moin/PythonDecoratorLibrary#Alternate_memoize_that_stores_cache_between_executions
# see: http://code.activestate.com/recipes/425445-once-decorator/
# TODO: fix doc and signature of decorate to match wrapped (1st link)

def dedupe(method):
    "A decorator that runs a method only if the first arument is doffernt to the last."
    attrname = "_%s_dedupe_result" % id(method)
    def decorated(self, *args, **kwargs):
        try:
            last_val = getattr(self, attrname)
            if last_val == args[0]:
                return None
        except AttributeError:
            setattr(self, attrname, args[0])

        return method(self, *args, **kwargs)
    return decorated



def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))





class CountdownTimer:
    """A resetable coundown timer that executes a callback when the timer expires."""

    def __init__(self, on_expiry_callback=None, interval_secs=3):
        self.keep_running = False
        self.exipry_time = 0
        self.interval_secs=interval_secs
        self.thread = None
        self.expired = False
        self.on_expiry_callback = on_expiry_callback

    def start(self):
        self.keep_running = True
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    def _start(self):
        while self.keep_running:
            if int(round(time())) > self.exipry_time and not self.expired and self.on_expiry_callback:
                self.on_expiry_callback()
                self.expired = True
            sleep(1)


    def reset(self):
        self.exipry_time = int(round(time())) + self.interval_secs
        self.expired = False


    def stop(self):
        self.keep_running = False



# slightly modified from: https://github.com/Coretec-Robotics/Tiny_4wd/blob/master/TinyPirate.py
def default_steering(inThrottle, inYaw):
    left = inThrottle + inYaw
    right = inThrottle - inYaw
    scaleLeft = abs(left / 127.0)
    scaleRight = abs(right / 127.0)
    scaleMax = max(scaleLeft, scaleRight)
    scaleMax = max(1, scaleMax)
    out_left = int(constrain(left / scaleMax, -127, 127))
    out_right = int(constrain(right / scaleMax, -127, 127))
    results = [out_left, out_right]
    return results



# see: http://www.impulseadventure.com/elec/robot-differential-steering.html
# Differential Steering Joystick Algorithm
# ========================================
#   by Calvin Hass
#   http://www.impulseadventure.com/elec/
#
# Converts a single dual-axis joystick into a differential
# drive motor control, with support for both drive, turn
# and pivot operations.

# INPUTS
#int     nJoyX;              // Joystick X input                     (-128..+127)
#int     nJoyY;              // Joystick Y input                     (-128..+127)

# OUTPUTS
#int     nMotMixL;           // Motor (left)  mixed output           (-128..+127)
#int     nMotMixR;           // Motor (right) mixed output           (-128..+127)

# CONFIG
# - fPivYLimt  : The threshold at which the pivot action starts
#                This threshold is measured in units on the Y-axis
#                away from the X-axis (Y=0). A greater value will assign
#                more of the joystick's range to pivot actions.
#                Allowable range: (0..+127)

def differential_steering(nJoyY, nJoyX, axis_max=100.0):
    fPivYLimit = 32.0

    nJoyY = -nJoyY # TODO: global config
    # TEMP VARIABLES
    nMotPremixL = 0    #Motor (left)  premixed output         (-128..+127)
    nMotPremixR = 0    # Motor (right) premixed output        (-128..+127)
    nPivSpeed   = 0    # Pivot Speed                          (-128..+127)
    fPivScale   = 0    # Balance scale b/w drive and pivot    (   0..1   )


    # Calculate Drive Turn output due to Joystick X input
    if nJoyY >= 0:
        # Forward
        nMotPremixL = axis_max if nJoyX>=0 else axis_max + nJoyX
        nMotPremixR = axis_max- nJoyX if nJoyX>=0 else axis_max
    else:
        # Reverse
        nMotPremixL = axis_max - nJoyX if nJoyX>=0 else axis_max
        nMotPremixR = axis_max if nJoyX>=0 else axis_max + nJoyX

    # Scale Drive output due to Joystick Y input (throttle)
    nMotPremixL = nMotPremixL * nJoyY/axis_max;
    nMotPremixR = nMotPremixR * nJoyY/axis_max;

    # Now calculate pivot amount
    #  - Strength of pivot (nPivSpeed) based on Joystick X input
    #  - Blending of pivot vs drive (fPivScale) based on Joystick Y input
    nPivSpeed = nJoyX
    fPivScale = 0.0 if abs(nJoyY)>fPivYLimit else 1.0 - abs(nJoyY)/fPivYLimit

    # Calculate final mix of Drive and Pivot
    nMotMixL = (1.0-fPivScale)*nMotPremixL + fPivScale*nPivSpeed
    nMotMixR = (1.0-fPivScale)*nMotPremixR + fPivScale*-nPivSpeed

    return int(nMotMixL), int(nMotMixR)

HAVE_SMBUS=False
try:
    import smbus
    HAVE_SMBUS = True
except ImportError:
    logger.warning("smbus library not found, maybe not installed? maybe running on Mac/Windows?")


def i2c_scan(bus_num=1):
    global HAVE_SMBUS
    if not HAVE_SMBUS:
        return []
    bus = smbus.SMBus(bus_num) # 1 indicates /dev/i2c-1
    devices = []
    for device in range(128):
        try:
            bus.read_byte(device)
            logger.info("Found i2c device at addr: {}".format(hex(device)))
            devices.append(device)
        except Exception: # exception if read_byte fails
            pass

    return devices




# Must run some activvites on the main thread, e.g. PyGame event polling

import queue
import threading

callback_queue = queue.Queue()

def mainthread_dispatch(func):
    callback_queue.put(func)

def wait_blocking():
    callback = callback_queue.get() #blocks
    callback()



_keep_running = True

def wait_nonblocking():
    global _keep_running
    while _keep_running:
        try:
            callback = callback_queue.get(False) #doesn't block
        except queue.Empty:
            break
        callback()


def main_loop():
    global _keep_running
    while _keep_running:
        wait_blocking()


def exit_main():
    global _keep_running
    _keep_running = False

if __name__ == '__main__':
    import doctest
    doctest.testmod()