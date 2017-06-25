#!/usr/bin/python3

# Example of using remote GPIO access with gpiozero, installing picraftzero on the target Pi is not required.
# For setup and more info see: https://gpiozero.readthedocs.io/en/docs-updates/remote_gpio.html

# Run using:
# GPIOZERO_PIN_FACTORY=PiGPIOPin PIGPIO_ADDR=raspberry.local python3 remote_gpiozero.py

# If env var not present then default them:
from os import environ
if 'GPIOZERO_PIN_FACTORY' not in environ:
    environ['GPIOZERO_PIN_FACTORY'] = 'PiGPIOPin'
    environ['PIGPIO_ADDR'] = 'raspberrypi.local'        # or IP address '192.168.1.108'

# ------------------------------------------------------------------------
# Carry on as normal...

from gpiozero import LED
from picraftzero import Joystick, Button, start

joystick = Joystick()                   # use the first available controller's rightmost joystick (required)
button0 = Button(0)                     # attach some buttons by id

led = LED(17)


def button0_pressed():
    print("on")
    led.on()

def button0_released():
    print("off")
    led.off()


# Use the gpiozero callback style:
button0.when_pressed = button0_pressed
button0.when_released= button0_released

# Or use the spiozero source/value style:
#led.source = button0.values


start()
