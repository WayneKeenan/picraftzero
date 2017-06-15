#!/usr/bin/python3

# see: https://github.com/CamJam-EduKit/EduKit3

from gpiozero import CamJamKitRobot
from picraftzero import Joystick, steering_mixer, scaled_pair, start

robot = CamJamKitRobot()
joystick = Joystick()

robot.source = scaled_pair(steering_mixer(joystick.values), -1.0, 1.0, input_min=-100, input_max=100)

start()
