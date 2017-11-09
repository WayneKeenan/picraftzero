#!/usr/bin/python3

from picraftzero import Joystick, Wheelbase, start
from picraftzero.utils import differential_steering

# A 'steering_mixer' is a function converts joystick x/y axis values to left/right motor values.
# This exmaple shows how to use your a custom steering mixer in place of the built-in 'steering_mixer'.

# A custom steering mixer
# Moving joystick right makes the motors go forward.
def my_steering_mixer(values):
    it = iter(values)
    while True:
        (yaw, throttle) = next(it)
        # call the built-in picraftzero 'differential_steering' mixer,
        # but swap the throttle (fwd/back) and yaw (left/right) parameters to get the desired 'right is forward' effect
        yield differential_steering(throttle, yaw)

        # if left/right are acting the opposite to what you expect, then invert the 'throttle' pramater
        # e.g. yield differential_steering(-throttle, yaw)


# Joystick axis range is:               (left/down) -100 .. 100 (right/up)
# Motors value range is:     (full speed backwards) -100 .. 100 (full speed forwards)

joystick = Joystick()                        # use the first available controller (e.g. Rock Candy, XBox360) or web client
motors = Wheelbase(left=1, right=0)  # left,right = logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)

# Connect the motor speeds (left, right) to the joysticks axes (x,y), via the custom 'steering mixer'
motors.source = my_steering_mixer(joystick.values)

start()
