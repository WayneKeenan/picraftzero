
import logging
logger = logging.getLogger(__name__)

from picraft.interfaces.hardware.providers import ServoProvider
from picraft.utils import dedupe

from picraft.thirdparty import piconzero as pz

# The firmware on the board has an idle timeout
class PiconzeroServo(ServoProvider):

    def __init__(self, servo_id):
        if servo_id not in [0,1]:
            raise ValueError("Servo id must be 0 or 1")

        self.last_angle = None
        self.servo_id = servo_id
        pz.init()
        pz.setOutputConfig(self.servo_id, 2)      # Set output mode to Servo

    def begin(self):
        pass

    def end(self):
        # TODO: move to at Piconzero libary
        pz.cleanup()

    #@dedupe
    def set_angle(self, angle):
        if angle == self.last_angle:
            return
        self.last_angle = angle
        logger.debug("Set Angle {}".format(angle))
        pz.setOutput(self.servo_id, angle)

    def attach(self):
        pass

    def detatch(self):
        pass


