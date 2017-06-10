PiCraftZero
===========

A simple Python interface for controlling robots using multiple types of physical and virtual controllers. 
Optionally supports camera video streaming for mono and stereo vision. Stereo viewer supports using a Google cardboard viewer and can use the phone's orientation to control a pan & tilt camera mount..


Status
======

This is a prototype and all feedback is welcomed, please raise a [GitHub issue]() for requests and bug reports.



Quick Start
===========

The current installation process isn't too flexible at the moment, please follow the instructions very closely.

Install pre-requisites:
```
sudo apt-get install -y libav-tools python3-picamera python3-ws4py
```

Download the Git repo:
 
```cd /home/pi
mkdir bubbleworks
cd bubbleworks
git clone https://github.com/WayneKeenan/
```

Run example:
````
cd picraftzero
python3 examples/tiny4wd.py
```


Open a web browser to: `http://raspberrypi.local:8000/` or `http://<IP>:8000/`



Examples
========


simple.py
*********

A basic robot that has 2 motors.
This example can be found [here](examples/tiny4wd.py).


```python
from picraftzero import Joystick, Wheelbase, steering_mixer, start

joystick= Joystick()                         
motors = Wheelbase(left=0, right=1)  

motors.source = steering_mixer(joystick.values)

start()
```

pantilt.py
**********


A basic robot that has 2 motors and a pan & tilt camera fitted.
The right hand side joystick on the physical or virtual (web page) joystick cotnrols the motors.
The left hand side joystick on the physical or virtual (web page) joystick cotnrols the pan/tilt.

If a cameara, or 2, is attached then there will be streaming video.
If the browser is on a phone then gyro reading can be sent to the Pi to control the pan/tilt servos.  This is especually useful when the phone is put in a Google Cardboard viewer as the pan/tilt servo will track your head movements.
 
 
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


