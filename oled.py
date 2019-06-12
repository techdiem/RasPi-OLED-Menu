from time import sleep
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from RPi import GPIO
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
# GPIO.add_event_detect(clk, GPIO.FALLING, callback=my_callback, bouncetime=130)
# GPIO.add_event_detect(sw, GPIO.FALLING, callback=my_callback, bouncetime=300)

#Setup OLED display
device = sh1106(i2c(port=1, address=0x3C))

#Setup Connection to Mopidy
client = musicpd.MPDClient()
client.connect(config.get('MPD', 'ip'), int(config.get('MPD', 'port')))

with canvas(device) as draw:
    draw.text((30, 40), "Hello World", fill="white")

while True:
    sleep(2)

GPIO.cleanup()
