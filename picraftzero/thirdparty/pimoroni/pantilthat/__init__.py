from sys import exit, version_info
import logging

logger = logging.getLogger(__name__)

try:
    from smbus import SMBus
except ImportError:
    if version_info[0] < 3:
        logger.warning("Falling back to mock SMBus. This library requires python-smbus. Install with: sudo apt-get install python-smbus")
    elif version_info[0] == 3:
        logger.warning("Falling back to mock SMBus. This library requires python3-smbus. Install with: sudo apt-get install python3-smbus")
    from picraftzero.thirdparty.mocks.raspiberrypi.rpidevmocks import Mock_smbusModule
    SMBus = Mock_smbusModule.SMBus


from .pantilt import PanTilt, WS2812, PWM, RGB, GRB, RGBW, GRBW

__version__ = '0.0.3'

pantilthat = PanTilt(i2c_bus=SMBus(1))

brightness = pantilthat.brightness

idle_timeout = pantilthat.idle_timeout

clear = pantilthat.clear

light_mode = pantilthat.light_mode

light_type = pantilthat.light_type

servo_one = pantilthat.servo_one

servo_pulse_max = pantilthat.servo_pulse_max

servo_pulse_min = pantilthat.servo_pulse_min

servo_two = pantilthat.servo_two

servo_enable = pantilthat.servo_enable

set_all = pantilthat.set_all

set_pixel = pantilthat.set_pixel

set_pixel_rgbw = pantilthat.set_pixel_rgbw

show = pantilthat.show

pan = pantilthat.servo_one

tilt = pantilthat.servo_two
