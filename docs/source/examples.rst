#Examples

### pantilt.py

A basic robot that has 2 motors and a pan & tilt camera mount fitted.


This example can be found [here](examples/pantilt.py)


```python

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


start()
```


The right hand side joystick on the physical or virtual (web page) joystick cotnrols the motors.
The left hand side joystick on the physical or virtual (web page) joystick cotnrols the pan/tilt.

If a camera, or 2, is attached then there can be streaming video available.
If the browser is on a phone then the gyro readings from it can be sent to the Pi to control the pan/tilt servos.  This is useful when the phone is put into a Google Cardboard viewer, the pan/tilt servo will track your head movements.




# Other examples


and you can find more of the PiCarftZero 'gpiozero flow programming' (source/values) examples [here](test/picraftzero_testcases.py)
