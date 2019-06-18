from time import sleep
from luma.core.render import canvas
from RPi import GPIO
from menubuilder import buildRadioMenu, buildMainMenu, buildIdle, menuUsed
from setuphandler import client, device
import initglobals

print(client.mpd_version)

#Main program
menu = buildIdle()

while True:
    counter = initglobals.counter
    oldcounter = initglobals.oldcounter
    activemenu = initglobals.activemenu
    #Scrolling through the menu
    if counter != oldcounter and counter <= len(menu) and counter >= 0:
        oldcounter = counter
        with canvas(device) as draw:
            menuUsed(draw, menu)
    elif counter > len(menu)-1:
        initglobals.counter = 0
    elif counter < 0:
        initglobals.counter = len(menu)

    #Select a menu entry
    if initglobals.trigger == True:
        initglobals.trigger = False
        #IDLE screen
        if activemenu == 0:
            menu = buildMainMenu()
        #main menu
        if activemenu == 1 and counter == 1:
            menu = buildRadioMenu()
        #radio menu
        elif activemenu == 2 and counter == 0:
            menu = buildMainMenu()

GPIO.cleanup()