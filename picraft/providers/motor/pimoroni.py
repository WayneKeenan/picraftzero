
import logging
logger = logging.getLogger(__name__)


from picraft.utils import arduino_map

from picraft.interfaces.hardware.providers import MotorProvider
from picraft.utils import dedupe

from picraft.thirdparty.pimoroni import explorerhat

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
        speed = arduino_map(speed, -128, 127, -100, 100)
        try:
            PimoroniExplorerHatMotor.motors[self.motor_id].speed(speed)
        except AttributeError as ae:
            logger.error("Pimoroni Explorer HAT error setting motor speed, perhaps the HAT is not attached?")


