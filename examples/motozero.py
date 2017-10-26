#!/usr/bin/python

from time import sleep
from os import environ

# See: https://thepihut.com/products/motozero
# See: https://pinout.xyz/pinout/motozero
# See: https://github.com/robotpy/robotpy-wpilib/blob/master/wpilib/wpilib/robotdrive.py

HOST='192.168.1.32'

HOLD_TIME = 1

USE_REMOTE_GPIOZERO = 1

# Set env vars before importing gpiozero.
if USE_REMOTE_GPIOZERO:
    if 'GPIOZERO_PIN_FACTORY' not in environ:
        environ['GPIOZERO_PIN_FACTORY'] = 'pigpio'
        environ['PIGPIO_ADDR'] =  HOST

from gpiozero import Motor, OutputDevice



# Setup

# on remote Pi:

# from: https://github.com/RPi-Distro/python-gpiozero/issues/586#event-1202814500  (TODO: update to gpiozero docs)
# sudo pigpiod                          # run standalon (ignores system settings for remote access)
# sudo systemctl start pigpiod          # start now

#==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-units ===
#Authentication is required to start 'pigpiod.service'.
#Multiple identities can be used for authentication:
# 1.  ,,, (pi)
# 2.  root
#Choose identity to authenticate as (1-2): 1

# sudo systemctl enable pigpiod         # start every boot


from gpiozero.mixins import SourceMixin,SharedMixin, EventsMixin
from gpiozero.devices import Device, CompositeDevice

class MotoZero():

    def __init__(self):

        self.motor1 = Motor(24, 27)
        self.motor1_enable = OutputDevice(5, initial_value=1)

        # motor2 = Motor(6, 22)
        self.motor2 = Motor(22, 6)
        self.motor2_enable = OutputDevice(17, initial_value=1)

        self.motor3 = Motor(23, 16)
        self.motor3_enable = OutputDevice(12, initial_value=1)

        self.motor4 = Motor(13, 18)
        self.motor4_enable = OutputDevice(25, initial_value=1)

        self.motors = (self.motor1,
                       self.motor2,
                       self.motor3,
                       self.motor4)

        self.motors_enable = (self.motor1_enable,
                              self.motor2_enable,
                              self.motor3_enable,
                              self.motor4_enable)


    def stop(self):
        for motor in self.motors:
            motor.stop()

    def forward(self):
        for motor in self.motors:
            motor.forward()

    def reverse(self):
        for motor in self.motors:
            motor.reverse()

    def motor_speed(self, motor, speed):
        self.motors[motor].value = speed

    def motor_speed(self, speed):
        for motor in self.motors:
            motor.value=speed


def selftest(hold_time, motozero):
    motozero.forward()
    sleep(hold_time)

    motozero.reverse()
    sleep(hold_time)

    motozero.stop()
    sleep(hold_time)

    motozero.motor_speeds(0.5)  # half speed forwards
    sleep(hold_time)

    motozero.motor_speeds(-0.5) # half speed backwards
    sleep(hold_time)

    motozero.motor_speeds(0)    # stop
    sleep(hold_time)


mz= MotoZero()
selftest(HOLD_TIME, mz)


