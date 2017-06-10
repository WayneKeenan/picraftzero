import abc

class ServoProvider(object):
    """Base class for a Servo provider."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def begin(self):
        raise NotImplementedError

    @abc.abstractmethod
    def end(self):
        raise NotImplementedError

    # angles are 0 - 180
    @abc.abstractmethod
    def set_angle(self, tilt_angle):
        raise NotImplementedError

    @abc.abstractmethod
    def detatch(self):
        raise NotImplementedError

    @abc.abstractmethod
    def attach(self):
        raise NotImplementedError

class MotorProvider:
    """Base class for a Motors provider."""
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def begin(self, motor_id):
        """Initialize the provider.  Must be called once before any other calls are made to the provider.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def end(self):
        """Shutdown the provider..
        """
        raise NotImplementedError


    @abc.abstractmethod
    def set_speed(self, speed):
        """Set the motors speed..  range  -100 .. 100.
        """
        raise NotImplementedError


