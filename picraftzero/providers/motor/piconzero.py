
from picraftzero.log import logger


from picraftzero.interfaces.hardware.providers import MotorProvider
from picraftzero.utils import dedupe
from picraftzero.thirdparty import piconzero as pz



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
        speed = constrain(speed, -100, 100)
        pz.setMotor(self.motor_id, speed)


