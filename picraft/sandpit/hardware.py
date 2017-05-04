import logging
logger = logging.getLogger(__name__)

from picraft.utils import CountdownTimer, constrain
from picraft.providers import get_motor_provider, get_servo_provider



class Hardware:

    def __init__(self):
        self.motor_timer = None
        Servo = get_servo_provider()
        Motor = get_motor_provider()
        self.motor_a = Motor(0)
        self.motor_b = Motor(1)
        self.pan_servo = Servo(0)
        self.tilt_servo = Servo(1)

    def start(self):
        self.motor_timer = CountdownTimer(self.stop_motors)
        self.motor_a.begin()
        self.motor_b.begin()
        self.motor_timer.start()
        self.set_motor_speeds(0, 0)
        self.pan_servo.begin()
        self.tilt_servo.begin()
        self.set_pan_tilt(90, 90)

    def stop(self):
        self.pan_servo.end()
        self.tilt_servo.end()
        self.motor_timer.stop()
        self.motor_a.end()
        self.motor_b.end()

    def set_motor_speeds(self, motor_a_speed, motor_b_speed):
        motor_a_speed = constrain(motor_a_speed, -128, 127)
        motor_b_speed = constrain(motor_b_speed, -128, 127)
        self.motor_a.set_speed(motor_a_speed)
        self.motor_b.set_speed(motor_b_speed)
        self.motor_timer.reset()

    def stop_motors(self):
        self.set_motor_speeds(0, 0)

    # 0  = min,  180 = max
    def set_pan_tilt(self, pan_angle, tilt_angle):
        pan_angle = constrain(pan_angle, 0, 180)
        tilt_angle = constrain(tilt_angle, 0, 180)

        self.pan_servo.set_angle(pan_angle)
        self.tilt_servo.set_angle(tilt_angle)





