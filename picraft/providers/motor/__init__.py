import logging

from picraft.interfaces.hardware.providers import MotorProvider

logger = logging.getLogger(__name__)


class Default(MotorProvider):

    def __init__(self, motor_id):
        self._motor_id = motor_id

    def begin(self):
        pass

    def end(self):
        pass

    def set_speed(self, speed):
        logger.debug("DefaultMotorProvider({}).set_speed({})".format(self._motor_id, speed))

