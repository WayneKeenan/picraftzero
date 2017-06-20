[![PyPI version](https://badge.fury.io/py/picraftzero.svg)](https://badge.fury.io/py/picraftzero) 
[![Build Status](https://travis-ci.org/WayneKeenan/picraftzero.svg?branch=master)](https://travis-ci.org/WayneKeenan/picraftzero) 
[![codecov](https://codecov.io/gh/WayneKeenan/picraftzero/branch/master/graph/badge.svg)](https://codecov.io/gh/WayneKeenan/picraftzero)

# PiCraftZero


PiCraftZero is:

 + a universal remote control supporting virtual (web) and physical (handheld) controllers.
 + a collection of gpiozero compatible Python components for:
   + receiving joystick updates
   + auto discovering and controlling i2c based motor & servo add-ons for the Raspberry Pi
   + 'steering mixers' for converting joystick axis values to motor speeds 
   + websocket messaging
 + a camera streaming server and web client for single or dual cameras where:
   + remote stereo viewing can use a mobile phone with Google Cardboard 
   + the mobile phones gyro can control a pan/tilt camera mount 
 
 + cross platform, tested to work on Pi, Linux, Mac & Windows.
 + able to run without any additional hardware (e.g. Pi HATs or joypads), handy for dev & testing.
 + able to use desktop connected gamepads and mobile paired gamepads if your PC or mobile webbrowser supports the HTML5 Gamepad API
  
  
 

 
 


# Example

This is example is for robot that has 2 motors. It can be control using game controllers and web browsers on most desktop and mobile platforms. 
If a camera is attached then video can be streamed to the client.  

 
```python
#!/usr/bin/python3

from picraftzero import Joystick, Wheelbase, steering_mixer, start

joystick= Joystick()                         
motors = Wheelbase(left=0, right=1)  

motors.source = steering_mixer(joystick.values)

start()
```

A commented version of the code can be found [here](examples/tiny4wd.py) along with other [examples](examples).
 
 
You can see it in action off-road [here](https://twitter.com/cannonfodder/status/875368943661318146). 
You can see a selection of physical, virtual controllers and remote camera viewer (inc. GoogleCardboard VR viewer) on various desktop and mobile form factors [here](https://youtu.be/pUz_y9WAkc8) and [here](https://youtu.be/DPYABspXSOo).

Below is a 'screenshot' of PiCraftZero running in the Chromium browser on a RaspberryPi fitted with a [Pimoroni HyperPixel](https://shop.pimoroni.com/collections/raspberry-pi/products/hyperpixel) touchscreen. The remote control is communicating via WiFi to the [Coretec Robotics Tiny4WD](http://www.core-tec.co.uk/tiny-4wd/) robot. 

![PiCraftZero on a HyperPixel controling are Coretec Tiny4WD][demopic]

[demopic]: docs/source/images/picraftzero_hyperpixel_tiny4wd.jpg


   
# Status

PiCraft is in beta and all feedback is welcomed. For any feature requests, questions and bug reports please raise a [GitHub issue](https://github.com/WayneKeenan/picraftzero/issues) 

This README is currently the only documentation fit for end-user consumption, please ignore the 'docs' folder as that is mostly a collection of badly formatted notes, and is very much a work in progress.  

Pleae note that whilst PiCraftZero is in beta the API's may change, breaking backwards compatibility.

# Quick Start - Installing on a Pi

This quick start kicks the tyres to check that basic things are ok, this will run standlone on many platforms but please refer to the notes section, as this is more fun when installed on a Pi with the Pi Camera and i2c enabled.

To install:

```bash
sudo apt-get update
sudo apt-get install -y libav-tools python3-picamera python3-ws4py python3-smbus python3-dev python3-pip
sudo pip3 install evdev cap1xxx picraftzero
```

To run the default PiCraftZero behaviour which supports controlling 2 motors and 2 servos, if available, run:
 
```bash
python3 -m picraftzero
```

Open a web browser, on almost any platform or browser, to: `http://raspberrypi.local:8000/` or `http://<IP>:8000/`

Click on the 'Single Camera' icon in the center of the toolbar.

The right hand side of the screen is virtual joystick used for motor control by default.
The left hand side of the screen is virtual joystick used for pan/tilt control by default, if available.

If you move the joysticks around then you should see logging info on the console and if motors and servos connected they should move.


# Notes

### Raspbian prerequisites:

Use `raspi-config` to:

- Enable Camera, 
- Enable i2c
- Set GPU memory to at least 128Mb

### Hardware prerequisites

PiCraft zero has been written to work on many popular platforms with or without the physical robot hardware. 

It uses auto-detection of common motor and servo controllers and will resort to using a 'just log a message' fallback if no actual hardware is detected.

A list of the hardware that can be used:

- A Motor Controller  (optional) e.g. Pimoroni Explorer pHAT or 4tronix Piconzero
- A Servo Controller  (optional) e.g. Pimoroni PanTilt HAT or 4tronix Piconzero
- Camera (optional)
- Joypad (optional) e.g. RockCandy
- Desktop, laptop, smartphone or tablet with a webbrowser

If your using a Piconzero pHAT then attach the pan servo to servo 0 and the tilt servo to servo 1.

If you need to flip the image because the camera image is upside down edit the PicraftZero config file:

```bash
sudo nano /etc/picraftzero.cfg
```

Add these lines:
```
[camera]
hflip=yes
vflip=yes
```


# Enhancements

There are a few useful changes that can be made: 
+ running as a service and 
+ using an alternative camera streaming service which has higher framerates than the bundled default in PiCraftZero


## Install UV4L Camera Service 

To use a camera streaming service which has low latency you need to:

+ Install and run Uv4L RaspiCam service
+ Update PiCraftZero config


Install UV4L:

```bash
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
echo 'deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main' | sudo tee --append /etc/apt/sources.list > /dev/null
sudo apt-get update
sudo apt-get install -y uv4l uv4l-raspicam  uv4l-raspicam-extras   uv4l-server
```


Backup and download UV4L config:

```bash
sudo mv /etc/uv4l/uv4l-raspicam.conf /etc/uv4l/uv4l-raspicam.conf.original 
sudo wget https://raw.githubusercontent.com/WayneKeenan/picraftzero/master/picraftzero/resources/config/uv4l-raspicam.conf  -O /etc/uv4l/uv4l-raspicam.conf

```

Then run:

```bash
sudo systemctl restart uv4l_raspicam
sudo systemctl status uv4l_raspicam
```

Check the output and look for: 
```   Active: active (running)```


You can verify UV4L working by going to [http://raspberrypi.local:8080/stream](http://raspberrypi.local:8080/stream)

You will need to stop and re-run the PiCraftZero script.


If you want to stop the camera service type:

```sudo systemctl stop uv4l_raspicam```


### Configure PiCraftZero camera URL


Add user defined config to use the UV4L server:


```bash
sudo wget https://raw.githubusercontent.com/WayneKeenan/picraftzero/master/picraftzero/resources/config/picraftzero_snippet_uv4l.cfg  -O /etc/picraftzero.cfg
```

Stop and re-run the default script:

```bash
python3 -m picraftzero
```

Press reload in your web browser. 


# Running as a service

The default PicraftZero script can be run as a systemd service.

It's also possible to configure PiCraftZero to use your own script, TODO:link.

### Systemd setup

Download, enable and start the PiCraftZero systemd service by running:

```bash
sudo wget https://raw.githubusercontent.com/WayneKeenan/picraftzero/master/picraftzero/resources/config/picraftzero.service  -O /etc/systemd/system/picraftzero.service
sudo systemctl enable picraftzero
sudo systemctl start picraftzero
```

To show the service status run:

```bash
sudo systemctl status -l picraftzero
```

To show the service log file run: 
```bash
sudo journalctl -u picraftzero
```

### Disabling the service

To disable the service run:
```bash
sudo systemctl stop picraftzero
sudo systemctl disable picraftzero
```

# Updates


When a new `picraftzero` module is published on PyPi run the following to update and restart:
 
```bash
sudo pip3 install --upgrade picraftzero
sudo systemctl restart picraftzero
sudo systemctl status -l picraftzero
```

To revert to a specific version, change the version at the end of the line in this example:

```bash
sudo pip3 install picraftzero==0.1.6
```

