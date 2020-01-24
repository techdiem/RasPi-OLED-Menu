#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import helperFunctions
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
        if helperFunctions.activemenu == 0: screens.idlescreen.draw(device)
        elif helperFunctions.activemenu == 1: screens.mainmenu.draw(device)
        elif helperFunctions.activemenu == 2: screens.radiomenu.draw(device, radiomenu)
        elif helperFunctions.activemenu == 3: screens.shutdownmenu.draw(device)
        elif helperFunctions.activemenu == 4: screens.playlistmenu.draw(device)

        #Send trigger event to active screen
        if helperFunctions.trigger == True:
            helperFunctions.trigger = False
            if helperFunctions.activemenu == 0: screens.idlescreen.trigger()
            elif helperFunctions.activemenu == 1: screens.mainmenu.trigger()
            elif helperFunctions.activemenu == 2: screens.radiomenu.trigger()
            elif helperFunctions.activemenu == 3: screens.shutdownmenu.trigger()
            elif helperFunctions.activemenu == 4: screens.playlistmenu.trigger()

        sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
        break

shutdown()