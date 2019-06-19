from RPi import GPIO
import configparser
import musicpd
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import initGlobals

client = musicpd.MPDClient()

#Setup OLED display
device = sh1106(i2c(port=1, address=0x3C))

#Load Config
config = configparser.ConfigParser()
config.read("settings.ini")

#Set up rotary encoder
clk = int(config.get('Pins', 'clk'))
dt = int(config.get('Pins', 'dt'))
sw = int(config.get('Pins', 'sw'))

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
clkLastState = GPIO.input(clk)

#Setup Connection to Mopidy
client.connect(config.get('MPD', 'ip'), int(config.get('MPD', 'port')))

#Interrupt handler for re
def menuaction(channel):
    print("Triggered")
    initGlobals.trigger = True

def rotary_detect(channel):  
    global clkLastState
    try:
        clkState = GPIO.input(clk)
        if clkState != clkLastState:
            dtState = GPIO.input(dt)
            if dtState != clkState:
                initGlobals.counter += 1
            else:
                initGlobals.counter -= 1
                clkLastState = clkState
    finally:
        print (initGlobals.counter)

GPIO.add_event_detect(clk, GPIO.FALLING, callback=rotary_detect, bouncetime=150)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=menuaction, bouncetime=300)