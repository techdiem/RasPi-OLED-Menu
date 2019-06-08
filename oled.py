from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from RPi import GPIO
from time import sleep

#Setup pins for rotary encoder
clk = 17
dt = 18
sw = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(clk, GPIO.FALLING  , callback=my_callback, bouncetime=130)
# GPIO.add_event_detect(sw, GPIO.FALLING  , callback=my_callback, bouncetime=300)

#Setup OLED display
device = sh1106(i2c(port=1, address=0x3C))

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")

while True:
    sleep(1)

GPIO.cleanup()