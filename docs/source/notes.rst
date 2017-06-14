=====
Notes
=====

.. currentmodule:: picraft

.. _keep-your-script-running:

Keep your script running
========================


The following file includes an  :func:`~picraft.zero.start()` to keep the
script alive::

    from picraft.zero import Joystick, Wheelbase, steering_mixer, start

    joystick= Joystick()
    wheelbase = Wheelbase(left=0, right=1)
    wheelbase.source = steering_mixer(joystick.values)

    start()





README




There is a Python robot/server-side API (based on GPIOZero flows) and a HTML/JS (Web) client.

Supports camera video streaming for mono and stereo vision via a cross platform web application over WiFi.
The stereo viewer supports using a Google cardboard viewer and can use the phone's orientation to control a pan & tilt camera mount.


The Python server is designed to run on a Pi but can it run on non-Pi platforms for testing wihout the target hardware.
The Web client runs on popular browsers for:  Mac, Windows, Linux, Pi, iOS and Android (on both phones and tablets)

The web client has 2 virtual joysticks and also supports keyboards and HTML5 GamePads.
USB Wireless Joypads connected to the Pi


