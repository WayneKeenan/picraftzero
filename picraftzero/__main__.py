#!/usr/bin/python3

from picraftzero.log import logger
# TODO: check config for 'service' entry for user script and tun that instead
from picraftzero.config import get_config

config = get_config()
script_file = config.get('service', 'script', fallback=None)

if script_file:
    logger.info("Running user script: {}".format(script_file))
    with open(script_file) as f:
        code = compile(f.read(), script_file, 'exec')
        exec(code)
        # user script is expected to exit with an error code or 0, so shouldnt reach here
        exit(1)


# see the `pantilt.py` example for more info.

from picraftzero import Wheelbase, PanTilt, Joystick, steering_mixer, scaled_pair, start, filter_messages, MessageReceiver, join_values
joystick_right= Joystick(0)
joystick_left = Joystick(1)
messages = MessageReceiver(port=8001)

wheelbase = Wheelbase(left=0, right=1)
pan_tilt = PanTilt(pan=0, tilt=1)

wheelbase.source = steering_mixer(joystick_right.values)
pan_tilt.source =  join_values(
    filter_messages(messages.values, type='PANTILT', id=0),
    scaled_pair(joystick_left.values, 180, 0, -100, 100)
)

if __name__ == '__main__':
    start()


