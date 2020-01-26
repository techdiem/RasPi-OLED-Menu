import platform
print("Starting OLED display on", platform.node(), ":")
print()

#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import helperFunctions
import globalParameters
from setupHandler import device, client, shutdown, radiomenu
from time import sleep
import screens.idlescreen
import screens.mainmenu
import screens.playlistmenu
import screens.radiomenu
import screens.shutdownmenu

while True:
    try:
        sleep(0.1)
        #Draw active screen to display
        if globalParameters.activemenu == 0: screens.idlescreen.draw(device)
        elif globalParameters.activemenu == 1: screens.mainmenu.draw(device)
        elif globalParameters.activemenu == 2: screens.radiomenu.draw(device, radiomenu)
        elif globalParameters.activemenu == 3: screens.shutdownmenu.draw(device)
        elif globalParameters.activemenu == 4: screens.playlistmenu.draw(device)

        #Send trigger event to active screen
        if globalParameters.trigger == True:
            globalParameters.trigger = False
            if globalParameters.activemenu == 0: screens.idlescreen.trigger()
            elif globalParameters.activemenu == 1: screens.mainmenu.trigger()
            elif globalParameters.activemenu == 2: screens.radiomenu.trigger()
            elif globalParameters.activemenu == 3: screens.shutdownmenu.trigger()
            elif globalParameters.activemenu == 4: screens.playlistmenu.trigger()

        sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
        break

shutdown()