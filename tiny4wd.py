from signal import pause
from picraft.zero import Joystick, Wheelbase, steering_mixer

# Joystick axis values are  (left/down)  -100 .. 100   (right/up)
# Motor expects for left and right:   (full speed backwards) -100  .. 100 (full speed forwards)

joystick= Joystick()   # find the first available controller (e.g. Rock Candy, PS3, PS4, Wii)
tiny4wd_motors = Wheelbase(left=0, right=1)  # left/right= logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)

# Connect the motor speeds (left, right) to the joysticks axis (x,y), via a 'steering mixer'
tiny4wd_motors.source = steering_mixer(joystick.values)

pause()
