#!/usr/bin/env bash

# SSH security
#/bin/rm -v /etc/ssh/ssh_host_*
#sudo dpkg-reconfigure openssh-server

# Camera

grep -q '^start_x=' $CONFIG && sed -i 's/^start_x=.*/start_x=1/' $CONFIG || echo 'start_x=1' >> $CONFIG
grep -q '^gpu_mem=' $CONFIG && sed -i 's/^gpu_mem=.*/gpu_mem=128/' $CONFIG || echo 'gpu_mem=128' >> $CONFIG
#grep -q '^disable_camera_led=' $CONFIG && sed -i 's/^disable_camera_led=.*/disable_camera_led=1/' $CONFIG || echo 'disable_camera_led=1' >> $CONFIG


# i2c python

sudo apt-get install python-smbus python3-smbus python-dev python3-dev
CONFIG=/boot/config.txt
grep -q '^dtparam=i2c1' $CONFIG && sed -i 's/^dtparam=i2c1.*/dtparam=i2c1=on/' $CONFIG || echo 'dtparam=i2c1=on' >> $CONFIG
grep -q '^dtparam=i2c1_arm' $CONFIG && sed -i 's/^dtparam=i2c1_arm.*/dtparam=i2c1_arm=on/' $CONFIG || echo 'dtparam=i2c1_arm=on' >> $CONFIG


# Pimoroni Explorer pHAT

sudo pip3 install cap1xxx

# Video stremaing
curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -
echo 'deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main' | sudo tee --append /etc/apt/sources.list > /dev/null
sudo apt-get update
sudo apt-get install -y uv4l uv4l-raspicam  uv4l-raspicam-extras   uv4l-server

#DOUBLECHECK, think this (camera) depends o the 2 i2c paramters being set
#DOUBLECHECK, maynot need this next line:
# sudo apt-get install uv4l-server uv4l-uvc uv4l-xscreen uv4l-mjpegstream uv4l-dummy uv4l-raspidisp

# WEBRTC

# PiZero sudo apt-get install uv4l-webrtc-armv6
# Other: sudo apt-get install uv4l-webrtc

# demode under: /usr/share/uv4l/demos/  after:  sudo apt-get install uv4l-demos

# TODO:
#sudo cp /etc/uv4l/uv4l-raspicam.conf /etc/uv4l/uv4l-raspicam.conf.original

sudo service uv4l_raspicam restart


# For linux Events based input:

#sudo pip install evdev
#sudo pip3 install evdev

sudo pip3 install -r requirements.txt

#curl https://get.pimoroni.com/zerolipo | bash

#sudo rpi-update 0065c82b95aed1150c19ff7a6244832f7a14fb3e
#sudo reboot
