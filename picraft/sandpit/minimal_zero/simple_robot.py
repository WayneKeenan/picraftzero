
from signal import pause

# Import PiCraft Zero, extensions built on top of gpiozero and includes
# additional custom (and cutomised third party) libraries
from picraft.zero import Wheelbase, Joystick, steering_mixer

# Find the first available joystick
joystick = Joystick()

# Create a robot wheelbase to control the motors.
# The left and right parameters are logical IDs of 'any'* i2c connected motor(s)
# *The under-the-hood auto-detection supports the Pimoroni Explorer pHAT
# and the PiConZero.
tiny4wd = Wheelbase(left=0, right=1)

# Using the gpiozero pattern of connecting devices using source and value 'flows',
# the motor speeds are set from Joystick axises vales via a joystick-axis
# to motor-speed converter.
# The 'flow' uses tuple pairs for passing along the axis and motor speeds
tiny4wd.source = steering_mixer(joystick.values)

# Play the music, light the lights...
pause()

#Here be dragons.


from signal import pause
from picraft.zero import Wheelbase, Joystick, steering_mixer
joystick = Joystick()
tiny4wd = Wheelbase(left=0, right=1)
tiny4wd.source = steering_mixer(joystick.values)
pause()
