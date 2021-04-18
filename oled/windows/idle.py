""" IDLE screen """
import datetime
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Idle(WindowBase):
    clockfont = ImageFont.truetype(settings.FONT_CLOCK, size=28)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=12)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.musicmanager = musicmanager

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            #Widgets
            if not self.musicmanager.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=Idle.faicons, fill="white")

            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill="white")

            #Currently playing song
            playing = self.musicmanager.nowplaying()
            try:
                draw.text((1, 23), playing["name"][0:15], font=Idle.font, fill="white")
                draw.text((1, 35), playing["title"][0:15], font=Idle.font, fill="white")
            except KeyError:
                pass

            draw.text((1, 48), "\uf65d", font=Idle.faicons, fill="white") #menu
            if self.musicmanager.source == "mpd":
                #Buttons
                draw.text((31, 48), "\uf04a", font=Idle.faicons, fill="white") #prev
                try:
                    if self.musicmanager.status()["state"] == "play":
                        draw.text((46, 48), "\uf04c", font=Idle.faicons, fill="white") #pause
                    else:
                        draw.text((46, 48), "\uf04b", font=Idle.faicons, fill="white") #play
                except KeyError:
                    pass
                draw.text((61, 48), "\uf04e", font=Idle.faicons, fill="white") #next

            #Selection line
            if self.counter == 0:
                draw.line((1, 61, 12, 61), width=2, fill="white")
            elif self.counter != 0 and self.musicmanager.source == "mpd":
                draw.line((31+(self.counter-1)*15, 61, 42+(self.counter-1)*15, 61),
                                                            width=2, fill="white")


    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            self.musicmanager.previous()
        elif self.counter == 2:
            self.musicmanager.playpause()
        elif self.counter == 3:
            self.musicmanager.next()

    def turn_callback(self, direction):
        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction
