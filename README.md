[![Build Status](https://travis-ci.org/WayneKeenan/picraftzero.svg?branch=master)](https://travis-ci.org/WayneKeenan/picraftzero)


# PiCraftZero


PiCraftZero is:

 + a universal remote control using virtual (web) and physical (handheld) controllers, and 
 + a Python library for receiving controller inputs, based on gpiozero's flow programming model (source/values)

  
# Status

This is a prototype and all feedback is welcomed, please raise a [GitHub issue](https://github.com/WayneKeenan/picraftzero/issues) for feature requests, questions and bug reports.


# Quick Start - Installing on a Pi

This quick start kicks the tyres to check that basic things are ok, this will run standlone on many platforms but please refer to the notes section, as this is more fun on a Pi with the Pi Camera and i2c enabled.

To install type in:

```bash
sudo apt-get update && sudo apt-get install -y libav-tools python3-picamera python3-ws4py python3-smbus python3-dev python3-pip
sudo pip3 install evdev cap1xxx picraftzero
```

To run the default PiCraftZero behaviour which supports controlling 2 motors and 2 servos, if available, run:
 
```bash
python3 -m picraftzero
```

Open a web browser, on *almost any* device, to: `http://raspberrypi.local:8000/` or `http://<IP>:8000/`

The browser shuld be in landscape mode (or ona  desktop the windows should be wider than taller)

Click on the 'Single Camera' icon in the center of the toolbar.

The right hand side of the screen is virtual joystick used for motor control by default.
The left hand side of the screen is virtual joystick ised for pan/tilt control by default, if available.

If you move the joysticks around then you should see logging info on screen and if motors and servos connected they should move.




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


# Example

A basic robot that has 2 motors, the example below can be found [here](examples/tiny4wd.py) with more comments.


```python
#!/usr/bin/python3

from picraftzero import Joystick, Wheelbase, steering_mixer, start

joystick= Joystick()                         
motors = Wheelbase(left=0, right=1)  

motors.source = steering_mixer(joystick.values)

start()
```

There are more in the [examples](examples) folder.
 
# Enhancements

There are a few changes that can be made such as running as a service and using an alternative camera streaming service that has low latency/high framerates.


## Install UV4L Camera Service 

To use a camera streaming service which has low latency you need to:

+ Install and run Uv4L RaspiCam service
+ Update PiCraftZero config


You will need to exit and re-run any running PiCraftZero python script.

Install UV4L:

```bash
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
echo 'deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main' | sudo tee --append /etc/apt/sources.list > /dev/null
sudo apt-get update
sudo apt-get install -y uv4l uv4l-raspicam  uv4l-raspicam-extras   uv4l-server
```


Backup the UV4L default config file:

```bash
sudo mv /etc/uv4l/uv4l-raspicam.conf /etc/uv4l/uv4l-raspicam.conf.original 
```

This block below is a single script action and should be executed as one single copy and paste: 
```bash
cat << 'EOF' | sudo tee /etc/uv4l/uv4l-raspicam.conf > /dev/null
driver = raspicam
auto-video_nr = yes
frame-buffers = 4
encoding = mjpeg
width = 640
height = 480
framerate = 24
quality = 7 
video-denoise = no
nopreview = no
fullscreen = no
preview = 480
preview = 240
preview = 320
preview = 240
EOF
```

Then run:

```bash
sudo service uv4l_raspicam restart
sudo service uv4l_raspicam status
```

Check the output and look for: 
```   Active: active (running)```

You can verify it's working by going to [http://raspberrypi.local:8080/stream](http://raspberrypi.local:8080/stream)

If you want to stop the camera service type:

```sudo systemctl stop uv4l_raspicam```


### Configure PiCraftZero


Overriding the default config to use the UV4L server,

This block below is a single script action and should be executed as one single copy and paste: 

```bash
cat << 'EOF' | sudo tee /etc/picraftzero.cfg > /dev/null
[hmd]
camera_mono_url=http://${WINDOW_LOCATION_HOSTNAME}:8080/stream/video.mjpeg
EOF
```


Now re-run the default script:
```bash
python3 -m picraftzero
```

And press reload in your web browser.



##

