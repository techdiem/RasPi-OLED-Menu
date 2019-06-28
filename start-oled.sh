#!/bin/bash

# Parameter
FILENAME='oled.py'
START="python3 $FILENAME"
SCREEN='oled'
OLEDPATH='/home/pi/oled'

#Starten
start() {
    if ps ax | grep -v grep | grep -v -i SCREEN | grep $FILENAME > /dev/null
    then
        echo 'Display läuft bereits'
    else
        echo 'Display wird gestartet'
        
        cd $OLEDPATH && screen -dmS $SCREEN $START
        sleep 7

        if ps ax | grep -v grep | grep -v -i SCREEN | grep $FILENAME > /dev/null
        then
            echo 'Display läuft nun'
        else
            echo 'Display konnte nicht gestartet werden'
        fi
    fi
}

# Stoppen
stop() {
    if ps ax | grep -v grep | grep -v -i SCREEN | grep $FILENAME > /dev/null
    then
        echo 'Display wird abgeschaltet'
        screen -S oled -X stuff ^C
        sleep 2

        if ps ax | grep -v grep | grep -v -i SCREEN | grep $FILENAME > /dev/null
        then
            echo 'Display konnte nicht ausgeschaltet werden'
        else
            echo 'Display ist ausgeschaltet'
        fi
    else
        echo 'Das Display ist bereits aus'
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        if ps ax | grep -v grep | grep -v -i SCREEN | grep $FILENAME > /dev/null
        then
            echo "Display läuft."
        else
            echo "Display läuft nicht."
        fi
        ;;
    *)
        echo "Benutzung: oled.sh {start|stop|restart|status}"
        exit 1
        ;;
esac
exit 0
