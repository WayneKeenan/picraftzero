
from picraftzero.log import logger


from picraftzero.interfaces.hardware.providers import MotorProvider
from picraftzero.utils import constrain
from picraftzero.utils import dedupe
from picraftzero.thirdparty import piconzero as pz




class PiconzeroMotor(MotorProvider):

    def __init__(self, motor_id):
        self.motor_id = motor_id
        self._last_speed = None
        pz.init()


    def begin(self):
        pass

    def end(self):
        pass

    #@dedupe
    def set_speed(self, speed):
        msg = "set_speed({}, {})".format(self.motor_id, speed)
        logger.debug(msg)
        if speed == self._last_speed:
            return
        self._last_speed = speed
        logger.info(msg)

        speed = constrain(speed, -100, 100)
        pz.setMotor(self.motor_id, speed)


