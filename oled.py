from time import sleep
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from RPi import GPIO
from PIL import ImageFont
import musicpd
import configparser

#Load Config
config = configparser.ConfigParser()
config.read("settings.ini")

#Setup pins for rotary encoder
clk = int(config.get('Pins', 'clk'))
dt = int(config.get('Pins', 'dt'))
sw = int(config.get('Pins', 'sw'))
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clkLastState = GPIO.input(clk)
counter = 0
oldcounter = -1
trigger = False
activemenu = 0 #When IDLE screen is ready, change to 0

def menuaction(channel):
    global trigger
    print("Triggered")
    trigger = True

def rotary_detect(channel):  
    global clkLastState
    global counter
    try:
        clkState = GPIO.input(clk)
        if clkState != clkLastState:
            dtState = GPIO.input(dt)
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
                clkLastState = clkState
    finally:
        print (counter)


GPIO.add_event_detect(clk, GPIO.FALLING, callback=rotary_detect, bouncetime=150)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=menuaction, bouncetime=300)


#Setup OLED display
device = sh1106(i2c(port=1, address=0x3C))

#Setup Connection to Mopidy
# client = musicpd.MPDClient()
# client.connect(config.get('MPD', 'ip'), int(config.get('MPD', 'port')))


def menuentry(draw, x, y, text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+12), outline=255, fill=0)
    draw.text((x+2, y+1), text, font=font, fill="white")

def drawmenu(draw, entries):
    position = 0
    for i in range(len(entries)):
        menuentry(draw, 6, 2+position*12, entries[i])
        position += 1

def buildMenu(menuid):
    global activemenu
    global counter
    global oldcounter
    activemenu = menuid
    counter = 0
    oldcounter = -1

def buildRadioMenu():
    buildMenu(2)
    menu = ["Sender1", "Sender2", "Sender3", "Sender4", "Sender5"]
    return menu

def buildMainMenu():
    buildMenu(1)
    menu = ["Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
    return menu

def buildIdle():
    buildMenu(0)
    menu = ["zurück", "2"]
    return menu

def menuUsed(draw, entries):
    global counter
    drawmenu(draw, entries)
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")


#Main program

menu = buildIdle()

while True:

    #Scrolling through the menu
    if counter != oldcounter and counter <= len(menu) and counter >= 0:
        oldcounter = counter
        with canvas(device) as draw:
            menuUsed(draw, menu)
    elif counter > len(menu)-1:
        counter = 0
    elif counter < 0:
        counter = len(menu)

    #Select a menu entry
    if trigger == True:
        trigger = False
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
