PiCraftZero
===========

A simple Python interface for controlling robots using multiple types of physical and virtual controllers. 
Optionally supports camera video streaming for mono and stereo vision. Stereo viewer supports using a Google cardboard viewer and can use the phone's orientation to control a pan & tilt camera mount..


Status
======

This is a prototype and all feedback is welcomed, please raise a [GitHub issue]() for requests and bug reports.



Quick Start
===========

This quick start is for the impatient to kick the tyres ASAP and check that things are ok, but, *please* read the notes section below too.

The current installation process isn't too flexible at the moment, please follow the instructions very closely.


Install software pre-requisites:
```
sudo apt-get install -y libav-tools python3-picamera python3-ws4py
sudo pip3 install evdev cap1xxx
```

Download PiCraftZero from the Git repo:
 
```bash
cd /home/pi
mkdir bubbleworks
cd bubbleworks
git clone https://github.com/WayneKeenan/picraftzero
```


Run example:


```bash
cd picraftzero
python3  examples/tiny4wd.py
```


You will see some logging to the console.
If you have a pimoroni Explorer pHAT attached you should see:

```Explorer pHAT detected...```


If you have a Piconzero attached you should see:

```i2c devices detected: [34]```  (nice eh!)



Open a web browser to: `http://raspberrypi.local:8000/` or `http://<IP>:8000/`

The right hand side of the screen is virtual joystick 0 (usually used for motor control)
The left hand side of the screen is virtual joystick 1 (usually used for pan/tilt control)

If you move the joysticks around then things should happen...

Notes
=====

After the quickstart runs ok then there improvements that can be made for better video streaming (using uv4l) and to run PicraftZero as a systemd service that automatically starts on boot. Docmeten her [TBD, add readthedocs url]


Installation hardware pre-requisites:

To control motors and servos the Pi should have a Pimoroni Explorer pHAT or 4Tronix Piconzer attached to the Pi, although this is not mandatory for PiCraftZero to operate. (At the time of writing the Explorer pHAT is the more tested PiCraftZero code path)

If you have a camera, you should have attached it before starting the Pi, this is optional.

If you have a RockCandy controller connect it before running the code, not mandatory as there are WebBrowser based virtual joysticks.


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

If a camera, or 2, is attached then there can be streaming video available.
If the browser is on a phone then the gyro readings from it can be sent to the Pi to control the pan/tilt servos.  This is useful when the phone is put into a Google Cardboard viewer, the pan/tilt servo will track your head movements.
 
 
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


Enhancements
============

Camera Streaming
================


```bash
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
echo 'deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main' | sudo tee --append /etc/apt/sources.list > /dev/null
sudo apt-get update
sudo apt-get install -y uv4l uv4l-raspicam  uv4l-raspicam-extras   uv4l-server
sudo cp scripts/uv4l-raspicam.conf /etc/uv4l/
sudo service uv4l_raspicam restart
sudo service uv4l_raspicam status
```

Check the output and look for: 
```   Active: active (running)```


```bash
cd ~/bubbleworks/picraftzero/
nano picraftzero/config.py
```

Change the `DEFAULT_MONO_URL` at the top of the file to look like this

```python
DEFAULT_MONO_URL="http://raspberrypi.local:8080/stream/video.mjpeg"
#DEFAULT_MONO_URL="ws://${WINDOW_LOCATION_HOSTNAME}:8084/"
```

Change `raspberrypi.local' to the hostname or IP of your Pi.


Running as a service
====================


```bash
cd  ~/bubbleworks/picraftzero/
sudo ./scripts/install_service.sh  scripts/services/picraftzero_www.service
```

To follow the logs type:

```bash
sudo journalctl -f -u picraftzero_www.service
```



To stop, start or restart the service:

```bash
sudo systemctl stop picraftzero_www
sudo systemctl start picraftzero_www
sudo systemctl restart picraftzero_www
```



Bonjour/Zeroconf
================

Adding [Apples Bonjour Print services](https://support.apple.com/kb/dl999?locale=en_GB) is optional but makes connecting to Pi's so much easier on Windows, it lets you use names line 'raspberypi.local'.  (The Pi has Bonjour installed by default these days)