import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory

gpiozero.Device.pin_factory = PiGPIOFactory()

from gpiozero import AngularServo
from time import sleep

print(gpiozero.Device.pin_factory)

pan = AngularServo(17, min_angle=-45, max_angle=45)
tilt = AngularServo(27, min_angle=-45, max_angle=45)


#while True:
print('start')
pan.angle = 0.0
tilt.angle = 0.0
sleep(5)
pan.angle = 40
tilt.angle = 40

sleep(5)

pan.detach()
tilt.detach()