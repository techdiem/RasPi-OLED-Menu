from time import sleep
from luma.core.render import canvas
from RPi import GPIO
from menuBuilder import buildRadioMenu, buildMainMenu, menuUsed, buildShutdownMenu, buildSavedMenu, drawIdle
from setupHandler import client, device
import initGlobals
from subprocess import call
import os
#from offlineMusicPlayer import *

menu = []
page = 0

def stopPlaying():
    client.pause()
    initGlobals.activemenu = 0
    print("Playback stopped")

def playRadioStation():
    try:
        client.play(page + counter-1)
    except:
        print("Error playing the station!")
    initGlobals.activemenu = 0
    initGlobals.counter = 0
    print("Playing station id", page + counter -1)

def shutdownSystem():
    print("Shutting down system")
    client.stop()
    device.cleanup()
    #Debug mail
    try:
        os.remove("/home/pi/olederrors.log")
    except:
        pass

    call("sudo shutdown -h now", shell=True)
    exit()

while True:
    try:
        counter = initGlobals.counter
        oldcounter = initGlobals.oldcounter
        activemenu = initGlobals.activemenu
        #Scrolling through the menu
        if activemenu != 0:
            with canvas(device) as draw:
                if counter != oldcounter and counter <= len(menu) and counter >= 0:
                    oldcounter = counter
                    loadmenu = []
                    for i in range(page, page + 5):
                        if len(menu) >= i + 1:
                            loadmenu.append(menu[i])
                    menuUsed(draw, loadmenu)
                if page + counter > page + 3 and len(menu) > 5:
                    page += 1
                    initGlobals.counter -= 1
                if page + counter > len(menu):
                    initGlobals.counter = 0
                    page = 0
                if counter < 0:
                    initGlobals.counter = 0
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
    except KeyboardInterrupt:
        print("Exiting...")
        break
        
GPIO.cleanup()