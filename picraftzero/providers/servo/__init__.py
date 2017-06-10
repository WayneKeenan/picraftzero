
from picraftzero.interfaces.hardware.providers import ServoProvider
from picraftzero.log import logger

class Default(ServoProvider):
    def __init__(self, servo_id):
        self.last_angle = None
        self._servo_id = servo_id


    def begin(self):
        pass

    def end(self):
        pass

    def set_angle(self, angle):
        logger.debug("DefaultServoProvider({}).set_angle({})".format(self._servo_id, angle))
        if angle == self.last_angle:
            return
        self.last_angle = angle

    def attach(self):
        pass

    def detatch(self):
        pass