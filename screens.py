from PIL import ImageFont
import math
import datetime
from time import sleep
from luma.core.render import canvas
from setupHandler import client
today_last_time = "Unknown"

#IDLE screen with clock and current playing song
class idle():

    #Used in main Loop to create the screen
    @staticmethod
    def draw(device):
        global today_last_time
        clockfont = ImageFont.truetype("fonts/kristenITC.ttf", size=35)
        font = ImageFont.truetype("fonts/calibri.ttf", size=12)
        fontawesome = ImageFont.truetype("fonts/fontawesome.ttf", size=12)
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M")
        if today_time != today_last_time:
            with canvas(device) as draw:
                today_last_time = today_time
                now = datetime.datetime.now()

                draw.text((20, 3), today_time, font=clockfont, fill="white")
                try:
                    playingInfo = client.currentsong()
                except:
                    playingInfo = {'title': 'Could not load name!'}
                if playingInfo != {}:
                    currentSong = playingInfo["title"]
                    draw.text((12, 48), currentSong[0:21], font=font, fill="white")
                    draw.text((0, 45), text="\uf001", font=fontawesome, fill="white")

    #Runs when button is pressed
    @staticmethod
    def trigger(self):
        pass

    #Runs when the rotary encoder is turned (counter changes)
    @staticmethod
    def action(self):
        pass