
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from signal import pause


from picraft.zero import MessageReceiver, Wheelbase, PanTilt, Joystick, filter_messages, \
    steering_mixer, join_values, scaled_pair

# Create a 'message receiver'  (Defaults to receiving messages via a WebSocket server)
# This also starts an embedded HTTP server for delivering content, e.g. HTML/JS joysticks.
# The (WebSocket) Messages are a simple dictionary with keys of:
#   'type'  => message type, e.g. 'JOYSTICK'
#   'id'    => a logical numeric identifier, e.g. 0 = 1st (or right hand side) joystick, 1 = 2nd etc....
#   'data'  => an array so it can easily be used as a tuple for later source/value processing

messages = MessageReceiver()

# Find joysticks/thumbsticks for speed controll and pan/tilt control
# First parameter is a logical id where 0 = right stick, 1 = left stick
# Defaults to joysticks/thumbpads on the first connected controller found
joystick_right= Joystick(0)
joystick_left = Joystick(1)

#joystick_messages = MessageEmitter(messages, type='JOYSTICK', id=0)

wheelbase = Wheelbase(left=0, right=1)  # left/right: logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)
pan_tilt = PanTilt(pan=0, tilt=1)       # pan/tilt  : logical id of i2c servo (auto-detected PanTilt HAT or PiConZero)

# The demo Web app has 2 virtual joysticks (id's 0 & 1) that support mouse (desktop) & touch (mobile)

# Joystick axis values are  (left/down)  -100 .. 100   (right/up)


wheelbase.source = steering_mixer(
    join_values(
        filter_messages(messages.values, type='JOYSTICK', id=0),
        joystick_right.values
    )
)

pan_tilt.source = join_values(
    filter_messages(messages.values, type='PANTILT', id=0),
    scaled_pair(
        join_values(joystick_left.values, filter_messages(messages.values, type='JOYSTICK', id=1)), 180, 0, -100, 100),
)

pause()

