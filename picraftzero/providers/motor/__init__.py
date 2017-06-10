
from picraftzero.interfaces.hardware.providers import MotorProvider

from picraftzero.log import logger


class Default(MotorProvider):

    def __init__(self, motor_id):
        self._motor_id = motor_id
        self._last_speed = None

    def begin(self):
        pass

    def end(self):
        pass

    def set_speed(self, speed):
        msg = "DefaultMotorProvider({}).set_speed({})".format(self._motor_id, speed)
        logger.debug(msg)
        if speed == self._last_speed:
            return
        logger.info(msg)
        self._last_speed = speed
