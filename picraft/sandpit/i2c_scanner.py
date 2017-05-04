#!/usr/bin/env python

import smbus

bus = smbus.SMBus(1) # 1 indicates /dev/i2c-1

for device in range(128):

      try:
         bus.read_byte(device)
         print(hex(device))
      except: # exception if read_byte fails
         pass
