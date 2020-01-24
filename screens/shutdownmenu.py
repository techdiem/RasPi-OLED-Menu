from PIL import ImageFont
from luma.core.render import canvas
import helperFunctions
from setupHandler import font_icons, font_text

#Shutdown menu (screenid: 3)
def draw(device):
    global font_text, font_icons
    font = ImageFont.truetype(font_text, size=12)
    faicons = ImageFont.truetype(font_icons, size=18)
    counter = helperFunctions.counter
    if counter != helperFunctions.oldcounter and counter <= 1 and counter >= 0:
        helperFunctions.oldcounter = counter
        with canvas(device) as draw:
            draw.text((5, 2), text="Wirklich ausschalten?", font=font, fill="white")
            if counter == 0:
                x = 15
                y = 22
            else:
                x = 84
                y = 22
            draw.rectangle((x, y, x+30, y+40), outline=255, fill=0)

            draw.text((18, 25), text="Nein", font=font, fill="white")
            draw.text((20, 40), text="\uf0a8", font=faicons, fill="white")

            draw.text((94, 25), text="Ja", font=font, fill="white")
            draw.text((90, 40), text="\uf011", font=faicons, fill="white")

    if counter > 1: helperFunctions.counter = 0
    if counter < 0: helperFunctions.counter = 0

def trigger():
    counter = helperFunctions.counter
    if counter == 0: helperFunctions.setScreen(1)
    elif counter == 1: helperFunctions.shutdownSystem()