#!/bin/sh

SERVICE=$1


echo Removing  service: $SERVICE

echo stoping first

systemctl stop $SERVICE
systemctl disable $SERVICE


rm /etc/systemd/system/$1


echo Done
echo ====

systemctl status $SERVICE

