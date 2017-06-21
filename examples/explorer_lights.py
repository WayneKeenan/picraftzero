#!/usr/bin/env python
# coding: Latin-1
# Load library functions we want

from picraftzero import Joystick, Wheelbase, steering_mixer, start

from picraftzero.thirdparty.pimoroni.explorerhat import output  # instead of: from explorerhat import output

joystick = Joystick()                  # use the first available controller (e.g. Rock Candy, XBox360) or web client
motors  = Wheelbase(left=0, right=1)   # left,right = logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)
motors.source = steering_mixer(joystick.values) # convert joystick axis to motor speeds


output.one.on()
output.two.on()

try:
    print('Press CTRL+C to quit')

    start()

except KeyboardInterrupt:
    output.one.off()
    output.two.off()

print("bye")
