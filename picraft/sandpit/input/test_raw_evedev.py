# see: http://ericgoebelbecker.com/2015/06/raspberry-pi-and-gamepad-programming-part-1-reading-the-device/
from evdev import InputDevice
from select import select
gamepad = InputDevice('/dev/input/event0')
while True:
    r,w,x = select([gamepad], [], [])
    for event in gamepad.read():
        print(event)

