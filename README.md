PiCraftZero
===========

A simple Python interface for controlling robots with physical and virtual controllers. 
Optionally with camera video streaming for mono and stero vision.


Goal
====
Make creating remote cntroles for robots easy and 




What can it do?
===============




Controller Use cases:

Motor control only (No Pan Tilt)
1. robot  +  rock candy 
2. robot  +  iPhone
3. robot  +  android tablet
4. robot  +  iPhone + Bluetooth Classic Keyboard
5. robot  +  iPhone + 8bitdo (Joypad appears as a Bluetooth Classic Keyboard)
6. robot  +  iPhone + BLE joypad

Motor and  Pan/Tilt  - Single Camera
1. robot  +  rock candy
2. robot  +  iPhone
3. robot  +  android tablet
4. robot  +  iPhone / BLE joypad


Motor and  Pan/Tilt  - Single Camera + VR HMD
1. robot + rock candy + google cardboard 

Motor and  Pan/Tilt  - Dual Camera + VR HMD
1. robot + rock candy + google cardboard


Autodetected i2c motor drivers (Explorer pHAT)

Based on GPIOZero flow based programming model (source/values)



Status
======
This is an early-stage experiment that I'm are developing out in the wild.
This *currently* may only be of interest to brave developers and end-users looking to provide feedback and/or to contribute.



Installation
============


git clone 




Examples
========


The public interface of PiCraftZero can be considered to just be:
 
1. On the server (Pi Robots) side: picraft/zero.py and picraft/picraft.cfg
2. On the client (Virtual Joystick/Viewer/HMD): resources/www/js/app.js, resources/www/js/lib/bubbleworks/*.js


Main
----

main.py
*******



tiny4wd.py
***********







Classic Blue not o iOS
BLE on iOS and Android bt effectively not yet on RPi

Wifi is the common denominator and (currently) better suited to video streaming.


Code:

1. Local Joystick + Motors
2. Local Joystick + Remote Joystick + Motors
3. Local Joystick + Remote Joystick + Motors + Servos
 


Acknowkledgements
=================

GPIO Zero - Bun NuttallDave

piStremaing
u4vl - 

MOtor Srivers: Phil @ Pimoroing & 4Tronix
 
JS Libs
Gyro,
Virtual Joystick

Pgame