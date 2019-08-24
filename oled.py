#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import screens
from setupHandler import device
from helperFunctions import activemenu, trigger

while True:
    try:
        #Draw active screen to display
        if activemenu == 0: screens.idlescreen.draw(device)
        elif activemenu == 1: screens.mainmenu.draw(device)
        elif activemenu == 2: screens.radiomenu.draw(device)
        elif activemenu == 3: screens.shutdownmenu.draw(device)
        elif activemenu == 4: screens.savedmenu.draw(device)

        #Send trigger event to active screen
        if trigger == True:
            trigger == False
            if activemenu == 0: screens.idlescreen.trigger()
            elif activemenu == 1: screens.mainmenu.trigger()
            elif activemenu == 2: screens.radiomenu.trigger()
            elif activemenu == 3: screens.shutdownmenu.trigger()
            elif activemenu == 4: screens.savedmenu.trigger()

    except KeyboardInterrupt:
        print("Exiting...")
        break
        
GPIO.cleanup()