
from picraftzero.log import logger


from picraftzero.utils import dedupe

# has its own idle timout (deafult 2 seconds)

from picraftzero.interfaces.hardware.providers import ServoProvider

HAVE_PANTILT = False
try:
    from picraftzero.thirdparty.pimoroni import pantilthat
    HAVE_PANTILT = True


    # has its own idle timout (deafult 2 seconds)
except OSError:
    logger.warn("Failed to initialise Pimoroni PanTilt HAT, is it attached?")

# TOOD: add a 'dummy' class if HAVE_PANTILT False , to remove   the 'if not HAVE_PANTILT' nonsense.

class PimoroniPanTiltServo_Real(ServoProvider):


    def __init__(self, servo_id):
        if servo_id not in [0,1]:
            raise ValueError("Servo id must be 0 or 1")

        self.last_angle = None
        self.servo_id = servo_id+1

        if servo_id == 0:
            self.set_servo_angle = pantilthat.servo_one
        elif servo_id == 1:
            self.set_servo_angle = pantilthat.servo_two


    def begin(self):
        self.attach()

    def end(self):
        self.detatch()

    #@dedupe
    def set_angle(self, angle):
        msg = "Set Angle {}".format(angle)
        logger.debug(msg)
        if angle == self.last_angle or angle is None:
            return
        logger.info(msg)
        self.last_angle = angle
        angle -= 90
        try:
            self.set_servo_angle(angle)
        except IOError as e:
            logger.exception("cant set angle")

    def attach(self):
        pantilthat.servo_enable(self.servo_id, True)

    def detatch(self):
        pantilthat.servo_enable(self.servo_id, False)


class PimoroniPanTiltServo_Fake(ServoProvider):

    def __init__(self, servo_id):
        logger.warn("Pan Tilt hat did not initialise on import, is it connected?")

    def begin(self):
        pass

    def end(self):
        pass

    #@dedupe
    def set_angle(self, angle):
        pass

    def attach(self):
        pass

    def detatch(self):
        pass


PimoroniPanTiltServo = PimoroniPanTiltServo_Real if HAVE_PANTILT else PimoroniPanTiltServo_Fake
