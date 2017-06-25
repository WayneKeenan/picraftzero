

# on pi:
"""
sudo wget https://raw.githubusercontent.com/joan2937/pigpio/master/util/pigpiod -O /etc/init.d/pigpiod
sudo chmod +x /etc/init.d/pigpiod
sudo update-rc.d pigpiod defaults
sudo service pigpiod start
sudo service pigpiod status
"""


# on 'desktop'
"""
git clone https://github.com/rpi-distro/python-gpiozero
virtualenv -p python3 gpiozero-env
source gpiozero-env/bin/activate
cd python-gpiozero
python setup.py develop
pip install pigpio
GPIOZERO_PIN_FACTORY=MockPin pip install picraftzero


GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=192.168.1.108 python
from gpiozero import LED
led = LED(17)
led.value=0.5
"""



from os import environ
environ['GPIOZERO_PIN_FACTORY'] = 'pigpio'
environ['PIGPIO_ADDR'] = 'raspberrypi.local'

#import gpiozero.devices
#from gpiozero.pins.pigpiod import PiGPIOPin
#gpiozero.devices.pin_factory = PiGPIOPin

from signal import pause
from gpiozero import LED

led = LED(17)
led.on()

pause()
