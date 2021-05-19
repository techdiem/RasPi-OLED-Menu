""" IDLE screen """
import datetime
import asyncio
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
        self._active = False
        self.musicmanager = musicmanager
        self._playingname = ""
        self._playingtitle = ""

    def activate(self):
        self._active = True
        self.loop.create_task(self._generatenowplaying())

    def deactivate(self):
        self._active = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            #Widgets
            if not self.musicmanager.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=Idle.faicons, fill="white")

            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill="white")

            #Currently playing song
            draw.text((1, 23), self._playingname, font=Idle.font, fill="white")
            draw.text((1, 35), self._playingtitle, font=Idle.font, fill="white")

            #Buttons
            draw.text((1, 48), "\uf65d", font=Idle.faicons, fill="white") #menu
            draw.text((31, 48), "\uf04a", font=Idle.faicons, fill="white") #prev

            if self.musicmanager.source == "mpd" and self.musicmanager.status() == "play":
                draw.text((46, 48), "\uf04c", font=Idle.faicons, fill="white") #pause
            elif self.musicmanager.source == "mpd":
                draw.text((46, 48), "\uf04b", font=Idle.faicons, fill="white") #play

            draw.text((61, 48), "\uf04e", font=Idle.faicons, fill="white") #next

            #Selection line
            if self.counter == 0:
                draw.line((1, 61, 12, 61), width=2, fill="white")
            elif self.counter > 0 and (self.counter < 2 or self.musicmanager.source == "mpd"):
                draw.line((31+(self.counter-1)*15, 61, 42+(self.counter-1)*15, 61),
                                                            width=2, fill="white")
            elif self.counter == 2 and self.musicmanager.source == "airplay":
                draw.line((31+(self.counter)*15, 61, 42+(self.counter)*15, 61),
                                                            width=2, fill="white")

    async def _generatenowplaying(self):
        namex = 0
        titlex = 0
        oldname = ""
        oldtitle = ""
        while self.loop.is_running() and self._active:
            playing = self.musicmanager.nowplaying()
            if "name" in playing:
                name = playing['name']
            elif "artist" in playing and "album" in playing:
                name = f"{playing['artist']} - {playing['album']}"
            else:
                name = ""

            if name == oldname and Idle.font.getsize(name[namex:])[0] > 127:
                namex += 1
            else:
                namex = 0
                oldname = name

            self._playingname = name[namex:]

            if "title" in playing:
                title = playing['title']
            else:
                title = ""

            if title == oldtitle and Idle.font.getsize(title[titlex:])[0] > 127:
                titlex += 1
            else:
                titlex = 0
                oldtitle = title
            self._playingtitle = title[titlex:]

            await asyncio.sleep(1)



    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            self.musicmanager.previous()
        elif self.counter == 2 and self.musicmanager.source == "mpd":
            self.musicmanager.playpause()
        elif self.counter == 2 and self.musicmanager.source == "airplay":
            self.musicmanager.next()
        elif self.counter == 3:
            self.musicmanager.next()

    def turn_callback(self, direction):
        if (self.counter + direction <= 3 and self.musicmanager.source == "mpd") or \
        (self.counter + direction <= 2 and self.musicmanager.source == "airplay") \
        and self.counter + direction >= 0:
            self.counter += direction
