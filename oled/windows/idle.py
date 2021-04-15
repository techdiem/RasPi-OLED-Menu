""" IDLE screen """
import datetime
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Idle(WindowBase):
    def __init__(self, windowmanager, mopidyconnection, shairportconnection):
        super().__init__(windowmanager)
        self.counter = 0
        self.mopidyconnection = mopidyconnection
        self.shairportconnection = shairportconnection

    def render(self):
        clockfont = ImageFont.truetype(settings.FONT_CLOCK, size=28)
        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=12)
        faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=22)

        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=clockfont, fill="white")

            #Currently playing song
            draw.text((0, 27), text="\uf001", font=faicons, fill="white") #music icon
            draw.text((12, 29), "Lalala hier ist ein Song", font=font, fill="white")


    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")

    def turn_callback(self, direction):
        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction

    def airplay_callback(self, info, nowplaying):
        pass
