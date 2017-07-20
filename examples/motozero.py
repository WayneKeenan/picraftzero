
# run on pi: sudo pigpiod

USE_REMOTE_GPIOZERO = 1

if USE_REMOTE_GPIOZERO:
    from os import environ
    if 'GPIOZERO_PIN_FACTORY' not in environ:
        environ['GPIOZERO_PIN_FACTORY'] = 'PiGPIOPin'
        environ['PIGPIO_ADDR'] = 'spinner.local'        # or IP address '192.168.1.108'



from gpiozero import Motor, OutputDevice
from time import sleep

# See: https://thepihut.com/products/motozero
# See: https://pinout.xyz/pinout/motozero
# See: https://github.com/robotpy/robotpy-wpilib/blob/master/wpilib/wpilib/robotdrive.py

motor1 = Motor(24, 27)
motor1_enable = OutputDevice(5, initial_value=1)
#motor2 = Motor(6, 22)
motor2 = Motor(22, 6)
motor2_enable = OutputDevice(17, initial_value=1)
motor3 = Motor(23, 16)
motor3_enable = OutputDevice(12, initial_value=1)
motor4 = Motor(13, 18)
motor4_enable = OutputDevice(25, initial_value=1)

motors = (motor1, motor2, motor3, motor4)

def selftest():
    for motor in motors:
        motor.forward()
        sleep(1)
        motor.stop()


    motor.forward()  # full speed forwards
    motor.forward(0.5)  # half speed forwards

    motor.backward()  # full speed backwards
    motor.backward(0.5)  # half speed backwards

    motor.stop()  # stop the motor

    motor.value = 0.5  # half speed forwards
    motor.value = -0.5  # half speed backwards
    motor.value = 0  # stop

    motor.reverse()  # reverse direction at same speed, e.g...

    motor.forward(0.5)  # going forward at half speed
    motor.reverse()  # now going backwards at half speed


selftest()


