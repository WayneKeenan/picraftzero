
from picraftzero.log import logger

from picraftzero.interfaces.hardware.providers import ServoProvider
from picraftzero.utils import dedupe

from picraftzero.thirdparty import piconzero as pz

# The firmware on the board has an idle timeout
class PiconzeroServo(ServoProvider):

    def __init__(self, servo_id):
        if servo_id not in [0,5]:
            raise ValueError("Servo id must be between 0 and 5")

        self.last_angle = None
        self.servo_id = servo_id
        pz.init()
        pz.setOutputConfig(self.servo_id, 2)      # Set output mode to Servo
        logger.info("Servo {} created".format(self.servo_id))

    def begin(self):
        pass

    def end(self):
        # TODO: move to at Piconzero libary
        pz.cleanup()

    #@dedupe
    def set_angle(self, angle):
        msg = "Set Angle {}".format(angle)
        logger.debug(msg)
        if angle == self.last_angle:
            return
        self.last_angle = angle
        logger.info(msg)
        pz.setOutput(self.servo_id, angle)

    def attach(self):
        pass

    def detatch(self):
        pass


