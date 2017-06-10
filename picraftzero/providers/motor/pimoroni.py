
from picraftzero.log import logger



from picraftzero.utils import constrain

from picraftzero.interfaces.hardware.providers import MotorProvider
from picraftzero.utils import dedupe

from picraftzero.thirdparty.pimoroni import explorerhat

class PimoroniExplorerHatMotor(MotorProvider):

    motors = [None, None]

    def __init__(self, motor_id):
        PimoroniExplorerHatMotor.motors[0] = explorerhat.motor.one
        PimoroniExplorerHatMotor.motors[1] = explorerhat.motor.two
        self.motor_id = motor_id



    def begin(self):
        pass

    def end(self):
        self.set_speed(0)

    #@dedupe
    def set_speed(self, speed):
        msg = "set_speed({}, {})".format(self.motor_id, speed)
        logger.debug(msg)

        speed = constrain(speed, -100, 100)

        try:
            PimoroniExplorerHatMotor.motors[self.motor_id].speed(speed)
            pass
        except AttributeError as ae:
            logger.error("Pimoroni Explorer HAT error setting motor speed, perhaps the HAT is not attached?")


