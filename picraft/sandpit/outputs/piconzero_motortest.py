from time import sleep

from picraft.thirdparty import piconzero as pz

pz.init(True, True)

pz.setMotor(0, 100)
sleep(1)
pz.setMotor(0,-50)
sleep(1)
pz.setMotor(0,0)
sleep(1)

pz.setMotor(1, 100)
sleep(1)
pz.setMotor(1,-50)
sleep(1)
pz.setMotor(1,0)
sleep(1)