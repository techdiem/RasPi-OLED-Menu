#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import helperFunctions
import screens
from setupHandler import device, client, radiomenu

while True:
    try:
        #Draw active screen to display
        if helperFunctions.activemenu == 0: screens.idlescreen.draw(device)
        elif helperFunctions.activemenu == 1: screens.mainmenu.draw(device)
        elif helperFunctions.activemenu == 2: screens.radiomenu.draw(device, radiomenu)
        elif helperFunctions.activemenu == 3: screens.shutdownmenu.draw(device)
        elif helperFunctions.activemenu == 4: screens.savedmenu.draw(device)

        #Send trigger event to active screen
        if helperFunctions.trigger == True:
            helperFunctions.trigger = False
            if helperFunctions.activemenu == 0: screens.idlescreen.trigger()
            elif helperFunctions.activemenu == 1: screens.mainmenu.trigger()
            elif helperFunctions.activemenu == 2: screens.radiomenu.trigger()
            elif helperFunctions.activemenu == 3: screens.shutdownmenu.trigger()
            elif helperFunctions.activemenu == 4: screens.savedmenu.trigger()

    except KeyboardInterrupt:
        print("Exiting...")
        break
        
GPIO.cleanup()