from time import sleep
from picraft.providers import get_motor_provider, get_servo_provider


print("\n=== Motor tests\n")

Motor = get_motor_provider()
motor_a = Motor(0)
motor_b = Motor(1)
motor_a.begin()
motor_b.begin()
print("Motor A - +100")
motor_a.set_speed(100)
sleep(2)
motor_a.set_speed(0)

print("Motor B - +100")
motor_b.set_speed(100)
sleep(2)
motor_b.set_speed(0)
motor_a.end()
motor_b.end()


sleep(2)
print("\n=== Servo tests\n")
Servo = get_servo_provider()
pan_servo = Servo(0)
tilt_servo = Servo(1)
pan_servo.begin()
tilt_servo.begin()

print("Pan/Tilt =  90/90")
pan_servo.set_angle(90)
tilt_servo.set_angle(90)
sleep(2)

print("Pan =  75")
pan_servo.set_angle(75)
sleep(2)
pan_servo.set_angle(90)
sleep(1)

print("Tilt =  75")
tilt_servo.set_angle(75)
sleep(2)
tilt_servo.set_angle(90)
sleep(1)
pan_servo.end()
tilt_servo.end()