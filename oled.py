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
trigger = 0

def menuaction(channel):
    print("Triggered")
    trigger = 1

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

def buildRadioMenu():
    menu = ["Sender1", "Sender2", "Sender3", "Sender4", "Sender5"]
    return menu

def buildMainMenu():
    menu = ["Wiedergabe stoppen", "Radio", "gespeicherte Musik", "Ausschalten"]
    return menu

def menuUsed(draw, entries):
    global counter
    drawmenu(draw, entries)
    draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")

while True:
    if counter != oldcounter and counter <= len(buildMainMenu()) and counter >= 0:
        oldcounter = counter
        with canvas(device) as draw:
            menuUsed(draw, buildMainMenu())
    elif counter > len(buildMainMenu())-1:
        counter = 0
    elif counter < 0:
        counter = len(buildMainMenu())


GPIO.cleanup()
