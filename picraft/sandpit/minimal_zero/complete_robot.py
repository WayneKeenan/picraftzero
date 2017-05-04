
from signal import pause

from picraft.zero import (MessageReceiver, Wheelbase, PanTilt, Joystick,
                          filter_messages, steering_mixer,
                          join_values, scaled_pair)

joystick_right= Joystick(0)
joystick_left = Joystick(1)

tiny4wd = Wheelbase(left=0, right=1)
pan_tilt = PanTilt(pan=0, tilt=1)

messages = MessageReceiver()        # WebSocket receiver

tiny4wd.source = steering_mixer(
    join_values(
        filter_messages(messages.values, type='JOYSTICK', id=0),
        joystick_right.values
    )
)

pan_tilt.source = join_values(
    filter_messages(messages.values, type='PANTILT', id=0),
    scaled_pair(
        join_values(joystick_left.values,
                    filter_messages(messages.values, type='JOYSTICK', id=1)),
        180, 0, -100, 100),
)

pause()

