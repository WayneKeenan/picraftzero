#!/usr/bin/python

from evdev import InputDevice, categorize, ecodes, KeyEvent

gamepad = InputDevice('/dev/input/event0')

for event in gamepad.read_loop():
    print()
    keyevent = categorize(event)
    print(event.type, keyevent, event.value)
