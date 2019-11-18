#Only avaiable on raspberry pi
try:
    from RPi import GPIO
except: pass
import configparser
import musicpd
import threading
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import helperFunctions
from time import sleep
import platform

from PIL import ImageFont
from luma.core.render import canvas

mpdconnected = False
mpdretries = 0

print("Starting OLED display on", platform.node(), ":")
print()

#Load Config
print("Load configuration file")
config = configparser.ConfigParser()
config.read("settings.ini")

#Set fonts
print("Loading font configuration")
font_icons = config.get('Fonts', 'icons')
font_text = config.get('Fonts', 'text')
font_clock = config.get('Fonts', 'clock')

#Functions for startscreen
def drawStart():
    global font_text, font_icons
    with canvas(device) as draw:
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=35)

        draw.text((25, 3), text="Wird gestartet...", font=font, fill="white")
        draw.text((50, 25), text="\uf251", font=fontawesome, fill="white")

def bigError(message):
    global font_text, font_icons
    with canvas(device) as draw:
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=35)

        if len(message) > 23:
            draw.text((5, 3), text=message[0:23], font=font, fill="white")
            draw.text((5, 12), text=message[23:], font=font, fill="white")
        else:
            draw.text((5, 3), text=message, font=font, fill="white")
        draw.text((50, 28), text="\uf071", font=fontawesome, fill="white")

#Setup OLED display
print("Connect to display")
device = sh1106(i2c(port=1, address=0x3C))
device.contrast(245)
drawStart() #User should have something to look at during start

#Set up rotary encoder
print("Set up rotary encoder")
clk = int(config.get('Pins', 'clk'))
dt = int(config.get('Pins', 'dt'))
sw = int(config.get('Pins', 'sw'))

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
current_clk = 1
current_dt = 1
LockRotary = threading.Lock() #create lock for rotary switch

#Setup Connection to Mopidy
print("Connect to Mopidy")
client = musicpd.MPDClient()

while not mpdconnected:
    if mpdretries <= 5:
        try:
            client.connect(config.get('MPD', 'ip'), int(config.get('MPD', 'port')))
            client.clear()
            client.load("[Radio Streams]")
            print("MPD version", client.mpd_version)

            print("Loading radio stations")
            savedStations = client.listplaylistinfo("[Radio Streams]")
            radiomenu = ["Zurück", ]
            for station in savedStations:
                radiomenu.append(station['title'])

            mpdconnected = True
        except:
            print("Error connecting to Mopidy! Retrying...")
            try: 
                client.disconnect() 
                #for the case when it is connected but
                #it isn't possible to load the radio stations
            except: pass
            sleep(2)
    else:
        print("Connection to MPD not possible. Exiting...")
        bigError("MPD Verbindung unterbrochen!")
        sleep(10)
        device.cleanup()
        exit()
    mpdretries += 1

#Interrupt handler for push button in rotary encoder
def menuaction(channel):
    helperFunctions.trigger = True

#Interrupt handler for turning the rotary encoder (changing the counter)
def rotary_detect(channel):  
    global current_clk, current_dt, LockRotary
    Switch_A = GPIO.input(clk)
    Switch_B = GPIO.input(dt)
    
    if current_clk == Switch_A and current_dt == Switch_B:
        #Same interrupt as before? -> Bouncing -> no actio
        pass
    else:
        #refresh saved state
        current_clk = Switch_A
        current_dt = Switch_B
        
        if (Switch_A and Switch_B): #both ones active
            LockRotary.acquire()
            if channel == dt: #Direction depends on which one was last
                helperFunctions.counter += 1
            else:
                helperFunctions.counter -= 1 #Set Counter
            LockRotary.release()


print("Attaching Interrupts")
#Rotary encoder
GPIO.add_event_detect(clk, GPIO.RISING, callback=rotary_detect)
GPIO.add_event_detect(dt, GPIO.RISING, callback=rotary_detect)
#Push Button
GPIO.add_event_detect(sw, GPIO.FALLING, callback=menuaction, bouncetime=300)

print("Setup finished")
print()