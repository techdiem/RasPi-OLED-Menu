import platform
print("Starting OLED display on", platform.node(), ":")
print()

#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except:
    print("This software needs to run on a RasPi, because it uses GPIO pins to communicate with the hardware.")
    exit()
import helperFunctions
import threading
from globalParameters import globalParameters
from setupHandler import device, client, shutdown
from time import sleep
import screens.idlescreen
import screens.mainmenu
import screens.playlistmenu
import screens.radiomenu
import screens.shutdownmenu
import screens.emptyscreen

updaterun = threading.Event()

while True:
    try:
        sleep(0.2)
        #Draw active screen to display
        if globalParameters.activemenu == 0: screens.idlescreen.draw(device)
        elif globalParameters.activemenu == 1: screens.mainmenu.draw(device)
        elif globalParameters.activemenu == 2: screens.radiomenu.draw(device)
        elif globalParameters.activemenu == 3: screens.shutdownmenu.draw(device)
        elif globalParameters.activemenu == 4: screens.playlistmenu.draw(device)
        elif globalParameters.activemenu == 5: screens.emptyscreen.draw(device)

        #Send trigger event to active screen
        if globalParameters.trigger == True:
            globalParameters.trigger = False
            if globalParameters.activemenu == 0: screens.idlescreen.trigger()
            elif globalParameters.activemenu == 1: screens.mainmenu.trigger()
            elif globalParameters.activemenu == 2: screens.radiomenu.trigger()
            elif globalParameters.activemenu == 3: screens.shutdownmenu.trigger()
            elif globalParameters.activemenu == 4: screens.playlistmenu.trigger()
            elif globalParameters.activemenu == 5: screens.emptyscreen.trigger(device) #Needs device to turn on screen

        #Run update procedure in separate thread
        if globalParameters.activemenu != globalParameters.oldactivemenu:
            globalParameters.oldactivemenu = globalParameters.activemenu
            updaterun.set()
            if globalParameters.activemenu == 0:
                updaterun.clear()
                updateThread = threading.Thread(target=screens.idlescreen.update, args=(updaterun,))
                updateThread.start()

        sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
        break

updaterun.set() #Stop screen update procedure
shutdown()