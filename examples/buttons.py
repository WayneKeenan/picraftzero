#!/usr/bin/python3

# Example of the experimental joypad button API, subject to change.

from picraftzero import Joystick, Button, start

joystick = Joystick()                   # use the first available controller's rightmost joystick (required)

button0 = Button(0)                     # attach some buttons by id
button1 = Button(1)
button2 = Button(2)
button3 = Button(3)


def button0_pressed():
    print('button0_pressed')

def button0_released():
    print('button0_released')

def button1_pressed():
    print('button1_pressed')

def button2_pressed():
    print('button2_pressed')

def button3_pressed():
    print('button3_pressed')

button0.when_pressed = button0_pressed
button0.when_released= button0_released
button1.when_pressed = button1_pressed
button2.when_pressed = button2_pressed
button3.when_pressed = button3_pressed


start()
