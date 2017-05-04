from time import sleep

from picraft.thirdparty.pimoroni import explorerhat


explorerhat.motor.one.speed(100)
sleep(1)
explorerhat.motor.one.speed(-50)
sleep(1)
explorerhat.motor.one.stop()
sleep(1)

explorerhat.motor.two.speed(100)
sleep(1)
explorerhat.motor.two.speed(-50)
sleep(1)
explorerhat.motor.two.stop()

