self.last_rot_x = 0
self.last_rot_y = 0
self.x_readings = [0, 0, 0, 0, 0]
self.y_readings = [0, 0, 0, 0, 0]


rot_x = message.data[0]
rot_y = message.data[1]

self.x_readings.insert(0, rot_x)
self.x_readings.pop()
rot_x = sum(self.x_readings) / len(self.x_readings)


self.y_readings.insert(0, rot_y)
self.y_readings.pop()
rot_y = sum(self.y_readings) / len(self.y_readings)

send = False

if abs(rot_x - self.last_rot_x) > 0.02:
    self.last_rot_x = rot_x
    send = True

if abs(rot_y - self.last_rot_y) > 0.02:
    self.last_rot_x = rot_x
    send = True

if send:
    self.publisher.publish([{'id': 1, 'value': rot_x}, {'id': 2, 'value': rot_y}])
