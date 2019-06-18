from time import sleep
from luma.core.render import canvas
from RPi import GPIO
from menuBuilder import buildRadioMenu, buildMainMenu, menuUsed, buildShutdownMenu, buildSavedMenu, drawIdle
from setupHandler import client, device
import initGlobals
from subprocess import call
#from offlineMusicPlayer import *

print(client.mpd_version)
menu = []

def stopPlaying():
    global menu
    client.stop()
    initGlobals.activemenu = 0

def playRadioStation():
    print("Starte Radio")

def shutdownSystem():
    print("System herunterfahren")
    device.cleanup()
    call("sudo shutdown -h now", shell=True)

while True:
    counter = initGlobals.counter
    oldcounter = initGlobals.oldcounter
    activemenu = initGlobals.activemenu
    #Scrolling through the menu
    if activemenu != 0:
        with canvas(device) as draw:
            if counter != oldcounter and counter <= len(menu) and counter >= 0:
                oldcounter = counter
                menuUsed(draw, menu)
            elif counter > len(menu)-1:
                initGlobals.counter = 0
            elif counter < 0:
                initGlobals.counter = len(menu)
    else:
        drawIdle(device)

    #Select a menu entry
    if initGlobals.trigger == True:
        initGlobals.trigger = False
        #IDLE screen
        if activemenu == 0: menu = buildMainMenu()
        #main menu
        elif activemenu == 1 and counter == 0: initGlobals.activemenu = 0
        elif activemenu == 1 and counter == 1: stopPlaying()
        elif activemenu == 1 and counter == 2: menu = buildRadioMenu()
        elif activemenu == 1 and counter == 3: menu = buildSavedMenu()
        elif activemenu == 1 and counter == 4: menu = buildShutdownMenu()
        #radio menu
        elif activemenu == 2 and counter == 0: menu = buildMainMenu()
        elif activemenu == 2 and counter != 0: playRadioStation()
        #shutdown menu
        elif activemenu == 3 and counter < 2: menu = buildMainMenu()
        elif activemenu == 3 and counter == 2: shutdownSystem()
        #offline music menu
        elif activemenu == 4 and counter == 0: menu == buildMainMenu()
        # elif activemenu == 4 and counter == 1: offlineMusicPlay()
        # elif activemenu == 4 and counter == 2: offlineMusicNext()
        # elif activemenu == 4 and counter == 3: offlineMusicPrev()
        

GPIO.cleanup()