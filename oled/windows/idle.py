""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
from ui.metabutton import MetaButton
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Idle(WindowBase):
    clockfont = ImageFont.truetype(settings.FONT_CLOCK, size=28)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=12)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager, musicmanager)
        self._active = False
        self._playingname = ""
        self._playingtitle = ""
        self._buttons = []
        self._selectedbtnindex = 0

    def activate(self):
        self._active = True
        self.loop.create_task(self._generatenowplaying())

    def deactivate(self):
        self._active = False

    def render(self):
        self._buttons = []

        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            #Volume
            draw.text((1,2), "\uf027", font=Idle.faicons, fill="white")
            draw.text((12,2), f"{str(self.musicmanager.volume)}%", font=Idle.font, fill="white")
            #Mopidy connection widget
            if not self.mopidyconnection.connected:
                draw.text((45, 2), "\uf071", font=Idle.faicons, fill="white")

            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill="white")

            #Currently playing song
            draw.text((1, 23), self._playingname, font=Idle.font, fill="white")
            draw.text((1, 35), self._playingtitle, font=Idle.font, fill="white")

            #Buttons
            self._buttons.append(MetaButton(1, 48, "\uf65d", lambda: self.windowmanager.set_window("mainmenu"))) #menu

            self._buttons.append(MetaButton(31, 48, "\uf04a", self.musicmanager.previous)) #prev

            if self.musicmanager.source == "mpd" and self.musicmanager.status() == "play":
                self._buttons.append(MetaButton(46, 48, "\uf04c", self.musicmanager.playpause)) #pause
            elif self.musicmanager.source == "mpd":
                self._buttons.append(MetaButton(46, 48, "\uf04b", self.musicmanager.playpause)) #play
            
            self._buttons.append(MetaButton(61, 48, "\uf04e", self.musicmanager.next)) #next

            #When button count changes, adjust selectedbtnindex
            if self._selectedbtnindex > len(self._buttons)-1:
                self._selectedbtnindex = len(self._buttons)-1
            
            #Draw buttons
            for button in self._buttons:
                draw.text((button.posx, button.posy), button.icon, font=Idle.faicons, fill="white")

            #Selection line
            btn = self._buttons[self._selectedbtnindex]
            draw.line((btn.posx, btn.posy+13, btn.posx+11, btn.posy+13), width=2, fill="white")


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

            if name == oldname and Idle.font.getlength(name[namex:]) > 127.0:
                namex += 1
            else:
                namex = 0
                oldname = name

            self._playingname = name[namex:]

            if "title" in playing:
                title = playing['title']
            else:
                title = ""

            if title == oldtitle and Idle.font.getlength(title[titlex:]) > 127.0:
                titlex += 1
            else:
                titlex = 0
                oldtitle = title
            self._playingtitle = title[titlex:]

            await asyncio.sleep(1)


    def push_callback(self):
        self._buttons[self._selectedbtnindex].trigger()

    def turn_callback(self, direction):
        if self._selectedbtnindex + direction <= len(self._buttons)-1 and \
            self._selectedbtnindex + direction >= 0:
            self._selectedbtnindex += direction
