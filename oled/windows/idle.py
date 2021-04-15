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
            #Widgets
            if not self.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=faicons, fill="white")

            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=clockfont, fill="white")

            #Currently playing song
            playing = self.mopidyconnection.nowplaying()
            try:
                draw.text((1, 23), playing["name"], font=font, fill="white")
                draw.text((1, 35), playing["title"], font=font, fill="white")
            except KeyError:
                pass

            #Buttons
            draw.text((1, 48), "\uf65d", font=faicons, fill="white") #menu
            draw.text((31, 48), "\uf04a", font=faicons, fill="white") #prev
            try:
                if self.mopidyconnection.status()["state"] == "play":
                    draw.text((46, 48), "\uf04c", font=faicons, fill="white") #pause
                else:
                    draw.text((46, 48), "\uf04b", font=faicons, fill="white") #play
            except KeyError:
                pass
            draw.text((61, 48), "\uf04e", font=faicons, fill="white") #next
            
            #Selection line
            if self.counter == 0:
                draw.line((1, 61, 12, 61), width=2, fill="white")
            else:
                draw.line((31+(self.counter-1)*15, 61, 42+(self.counter-1)*15, 61), width=2, fill="white")


    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            self.mopidyconnection.previous()
        elif self.counter == 2:
            self.mopidyconnection.playpause()
        elif self.counter == 3:
            self.mopidyconnection.next()

    def turn_callback(self, direction):
        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction

    def airplay_callback(self, info, nowplaying):
        pass
