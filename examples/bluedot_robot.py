#!/usr/bin/python3

# To install and setup pairing see: http://bluedot.readthedocs.io/en/latest/gettingstarted.html

# Add the following to either: ~/.picraftzero.cfg or /etc/picraftzero.cfg
# [joystick]
# use_bluedot=yes


# The following is exactly the same as the tiny4wd.py example, just with much less commenting here.

from picraftzero import Joystick, Wheelbase, steering_mixer, start

# use the first available controller joypad, webclient or BlueDot if installed and enabled in config
joystick = Joystick()

motors = Wheelbase(left=1, right=0)
motors.source = steering_mixer(joystick.values)

start()
