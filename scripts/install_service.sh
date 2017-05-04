#!/bin/bash

func_check_for_root() {
    if [ ! $( id -u ) -eq 0 ]; then
        echo "ERROR: $0 Must be run as root, Script terminating" ;exit 7
    fi
}

func_check_for_root

FILEPATH=$1

find . -name '*.sh' -exec chmod a+x '{}' ';'

SERVICE_FILE=$(basename "$FILEPATH")
#extension="${SERVICE_FILE##*.}"
SERVICE="${SERVICE_FILE%.*}"


echo Installing  service: $SERVICE from $FILEPATH


echo stoping $SERVICE

systemctl stop $SERVICE
systemctl disable $SERVICE


cp $FILEPATH  /etc/systemd/system/
systemctl enable $SERVICE
systemctl start $SERVICE
systemctl daemon-reload

sleep 3
#journalctl -u $SERVICE.service

systemctl status $SERVICE

echo Done
echo ====

