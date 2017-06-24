#!/usr/bin/python3

from picraftzero import Wheelbase, PanTilt, Joystick, steering_mixer, scaled_pair, start, filter_messages, MessageReceiver, join_values

# Find joysticks/thumbsticks for speed controll and pan/tilt control
# First parameter is a logical id where 0 = right stick, 1 = left stick
# Defaults to joysticks/thumbpads on the first controller found
# The joysticks could be on a 'physical' controller (e.g. Rock Candy) or a virtual joystick on the webapp

# The demo Web app has 2 virtual joysticks (id's 0 & 1) that support mouse (desktop) & touch (mobile)

# Joystick axis values are  (left/down)  -100 .. 100   (right/up)

joystick_right= Joystick(0)
joystick_left = Joystick(1)

messages = MessageReceiver(port=8001)

# Motor assume for left and right:   (full speed backwards) -100  .. 100 (full speed forwards)
wheelbase = Wheelbase(left=1, right=0)  # left/right= logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)
pan_tilt = PanTilt(pan=0, tilt=1)       # pan/tilt  = logical id of i2c servo (auto-detected PanTilt HAT or PiConZero)


# Connect the motor speeds (a,b) to the joysticks axis (x,y), via conversion
wheelbase.source = steering_mixer(joystick_right.values)
pan_tilt.source =  join_values(
    filter_messages(messages.values, type='PANTILT', id=0),
    scaled_pair(joystick_left.values, 180, 0, -100, 100)
)


start()


