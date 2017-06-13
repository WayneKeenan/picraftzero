
from picraftzero.log import logger

from picraftzero.utils import i2c_scan

setup_complete = False

_motor_provider_class = None
_servo_provider_class = None

def find_devices_and_import():

    global setup_complete, _motor_provider_class, _servo_provider_class
    if setup_complete:
        return
    devices = i2c_scan()            # TODO: add config option to specify i2c bus
    logger.info("i2c devices detected: {}".format(devices))

    PICONZERO_I2C_DEVICE_ID = 0x22
    PIMORONI_PANTILT_HAT_I2C_DEVICE_ID = 0x15
    PIMORONI_EXPLORER_PHAT_DEVICE_ID = 0x48        # THis is actually the on-board ADS


    from .motor import Default as Motor
    from .servo import Default as Servo

    if PICONZERO_I2C_DEVICE_ID in devices:
        from .motor.piconzero import PiconzeroMotor as Motor
        from .servo.piconzero import PiconzeroServo as Servo
    else:
        if PIMORONI_PANTILT_HAT_I2C_DEVICE_ID in devices:
            from .servo.pimoroniservo import PimoroniPanTiltServo as Servo

        if PIMORONI_EXPLORER_PHAT_DEVICE_ID in devices:
            from .motor.pimoroni import PimoroniExplorerHatMotor as Motor

    _motor_provider_class = Motor
    _servo_provider_class = Servo
    setup_complete = True



def get_motor_provider():
    find_devices_and_import()
    return _motor_provider_class


def get_servo_provider():
    find_devices_and_import()
    return _servo_provider_class
