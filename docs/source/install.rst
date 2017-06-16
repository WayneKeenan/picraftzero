# Installation


Once you have confirmed that the quickstart runs ok then there improvements that can be made for better video streaming (using uv4l) and to run PicraftZero as a systemd service that will automatically starts on boot.


Installation hardware pre-requisites:

- To control motors and servos the Pi should have a Pimoroni Explorer pHAT or 4Tronix Piconzero attached to the Pi, although this is not mandatory for PiCraftZero to operate.

- Using a camera is optional, if one is attached a webserver will be started to stream video (PiStremaing).

- If you have a RockCandy controller connect it before running the examples, it's not mandatory as there are WebBrowser based virtual joysticks.





# Pi /boot/config.txt config
## Camera

CONFIG=/boot/config.txt
grep -q '^start_x=' $CONFIG && sed -i 's/^start_x=.*/start_x=1/' $CONFIG || echo 'start_x=1' >> $CONFIG
grep -q '^gpu_mem=' $CONFIG && sed -i 's/^gpu_mem=.*/gpu_mem=128/' $CONFIG || echo 'gpu_mem=128' >> $CONFIG
#grep -q '^disable_camera_led=' $CONFIG && sed -i 's/^disable_camera_led=.*/disable_camera_led=1/' $CONFIG || echo 'disable_camera_led=1' >> $CONFIG

## i2c python

CONFIG=/boot/config.txt
grep -q '^dtparam=i2c1' $CONFIG && sed -i 's/^dtparam=i2c1.*/dtparam=i2c1=on/' $CONFIG || echo 'dtparam=i2c1=on' >> $CONFIG
grep -q '^dtparam=i2c1_arm' $CONFIG && sed -i 's/^dtparam=i2c1_arm.*/dtparam=i2c1_arm=on/' $CONFIG || echo 'dtparam=i2c1_arm=on' >> $CONFIG





## Software prerequisites

The only mandatory python requiement is gpiozero. But to use the good stuff like cameras, motor drivers then some other libraries need isntalling



### Motor driver library prerequisites

```bash
sudo pip3 install evdev             # Prefered library for Joystick handling on Pi/LInux
sudo pip3 install cap1xxx           # Needed for Pimoroni explorer
```

### Basic camera streaming prerequisites
```bash
sudo apt-get install -y libav-tools python3-picamera python3-ws4py
```


### Controlelrs prerequisites

Pygame may be needed on most non-Pi/Linux platforms:


```bash
sudo pip3 install pygame
```



# Run an example:

```bash
```


You will see some logging appear on the console.

If you have a Pimoroni Explorer pHAT attached you should see:

```Explorer pHAT detected...```


If you have a Piconzero attached you should see:

```i2c devices detected: [34]```



### Bonjour/Zeroconf


Adding [Apples Bonjour Print services](https://support.apple.com/kb/dl999?locale=en_GB) is optional but makes connecting to Pi's so much easier on Windows, it lets you use names line 'raspberypi.local'.  (The Pi has Bonjour installed by default these days)








### Running your own script as a service

Edit the PicraftZero config file:

```bash
sudo nano /etc/picraftzero.cfg
```

Add these lines:
```
[service]
script=/home/pi/my_picraftzero.py
```

Follow the log file, in the background, before you restart the service:
```bash
sudo journalctl -f -u picraftzero &
```

Restart the service:
```bash
sudo systemctl restart picraftzero
```

You should see in the logs something like:

```
... Running user script: /home/pi/my_picraftzero.py
```

Your script will now run instead of the default PiCraftZero script every time the Pi boots.
