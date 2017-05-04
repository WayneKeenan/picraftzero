
import logging
logger = logging.getLogger(__name__)

from picraft.interfaces.hardware.providers import MotorProvider
from picraft.utils import dedupe
from picraft.thirdparty import piconzero as pz



class PiconzeroMotor(MotorProvider):

    def __init__(self, motor_id):
        self.motor_id = motor_id
        pz.init()


    def begin(self):
        pass

    def end(self):
        pass

    #@dedupe
    def set_speed(self, speed):
        logger.debug("set_speed({}, {})".format(self.motor_id, speed))
        pz.setMotor(self.motor_id, speed)


