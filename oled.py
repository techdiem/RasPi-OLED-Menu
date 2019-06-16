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

def menuaction(channel):
    print("Triggered")
    font = ImageFont.load_default()
    global counter
    
    if counter == 1:
        counter = -2
        with canvas(device) as draw:
            draw.text((20, 30), "Menü 1", font=font, fill="white")
    elif counter == 2:
        counter = -2
        with canvas(device) as draw:
            draw.text((20, 30), "Menü 2", font=font, fill="white")
    elif counter == -2:
        counter = 0


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

while True:
    if counter != oldcounter and counter <= 4 and counter >= 0:
        oldcounter = counter
        with canvas(device) as draw:
            mainmenu = ["Test 1", "Noch ein Eintrag", "Ich bins", "Noch Einer", "Nummero 5"]
            drawmenu(draw, mainmenu)
            # draw.polygon(((0, 2), (0, 10), (5, 6)), fill="white")
            draw.polygon(((0, 2+counter*12), (0, 10+counter*12), (5, 6+counter*12)), fill="white")
    elif counter == 5:
        counter = 0
    elif counter == -1:
        counter = 4


GPIO.cleanup()
