""" IDLE screen """
import datetime
from ui.windowbase import WindowBase
from ui.metabutton import MetaButton
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Idle(WindowBase):
    clockfont = ImageFont.truetype(settings.FONT_CLOCK, size=28)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=12)
    widgeticon = ImageFont.truetype(settings.FONT_ICONS, size=14)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager, musicmanager)
        self._active = False
        self._playingname = ""
        self._playingtitle = ""
        self._nameoffset = 0.0
        self._titleoffset = 0.0
        self._namewidth = 0
        self._titlewidth = 0
        self._scroll_speed = 16.0
        self._scroll_gap = 16.0
        self._lastclockminute = ""
        self._source = self.musicmanager.source
        self._playstate = self.musicmanager.status() or ""
        self._volume = self.musicmanager.volume
        self._widgeticon = ""
        self._mopidy_connected = self.mopidyconnection.connected
        self._lastplaypauseicon = "\uf04b"
        self._buttons = [
            MetaButton(1, 48, "\uf7c0", lambda: self.windowmanager.set_window("radiomenu")),
            MetaButton(41, 49, "\uf04a", self.musicmanager.previous),
            MetaButton(57, 48, "\uf04b", self.musicmanager.playpause),
            MetaButton(71, 49, "\uf04e", self.musicmanager.next),
            MetaButton(112, 48, "\uf011", lambda: self.windowmanager.set_window("shutdownmenu")),
        ]
        self._selectedbtnindex = 0

        if self.eventbus is not None:
            self.eventbus.subscribe("audio.volume", self._on_volume)
            self.eventbus.subscribe("mopidy.connection", self._on_mopidy_connection)
            self.eventbus.subscribe("music.playstate", self._on_playstate)
            self.eventbus.subscribe("music.source", self._on_source)
            self.eventbus.subscribe("music.nowplaying", self._on_nowplaying)

    def activate(self):
        self._active = True
        self._sync_control_icons()
        self._on_nowplaying(self.musicmanager.nowplaying())
        self.mark_dirty()

    def deactivate(self):
        self._active = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            #Volume
            draw.text((1,2), "\uf027", font=Idle.faicons, fill="white")
            draw.text((12,2), f"{str(self._volume)}%", font=Idle.font, fill="white")
            #Connection widget
            draw.text((45, 4), self._widgeticon, font=Idle.widgeticon, fill="white")

            #Current time
            draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill="white")

            #Currently playing song
            draw.text((1 - int(self._nameoffset), 23), self._playingname, font=Idle.font, fill="white")
            draw.text((1 - int(self._titleoffset), 35), self._playingtitle, font=Idle.font, fill="white")

            #Draw buttons
            for button in self._buttons:
                draw.text((button.posx, button.posy), button.icon, font=Idle.faicons, fill="white")

            #Selection line
            btn = self._buttons[self._selectedbtnindex]
            draw.line((btn.posx, btn.posy+13, btn.posx+11, btn.posy+13), width=2, fill="white")

    @staticmethod
    def _extract_name_title(playing):
        if "name" in playing:
            name = playing['name']
        elif "artist" in playing and "album" in playing:
            name = f"{playing['artist']} - {playing['album']}"
        else:
            name = ""

        if "title" in playing:
            title = playing['title']
        else:
            title = ""
        return name, title

    def _sync_control_icons(self):
        showskipicons = False
        playpauseicon = ""

        if not self._mopidy_connected:
            if self._widgeticon != "\uf071":
                self._widgeticon = "\uf071"
                self.mark_dirty()
        elif self._source == "mpd" and self._playstate in ["play", "pause"]:
            if self._playstate == "play":
                playpauseicon = "\uf04c"
            else:
                playpauseicon = "\uf04b"
            showskipicons = True
            if self._widgeticon != "\ue585":
                self._widgeticon = "\ue585"
                self.mark_dirty()
        elif self._source == "airplay":
            if self._widgeticon != "\uf3cd":
                self._widgeticon = "\uf3cd"
                self.mark_dirty()
        else:
            if self._widgeticon != "":
                self._widgeticon = ""
                self.mark_dirty()
        
        if playpauseicon != self._lastplaypauseicon:
            self._lastplaypauseicon = playpauseicon
            self._buttons[2].icon = playpauseicon
            if showskipicons:
                self._buttons[1].icon = "\uf04a"
                self._buttons[3].icon = "\uf04e"
            else:
                self._buttons[1].icon = ""
                self._buttons[3].icon = ""
            self.mark_dirty()

    def _on_volume(self, volume):
        if volume is None:
            return
        if self._volume != volume:
            self._volume = volume
            self.mark_dirty()

    def _on_mopidy_connection(self, connected):
        if connected is None:
            return
        if self._mopidy_connected != connected:
            self._mopidy_connected = connected
            self.mark_dirty()
        self._sync_control_icons()

    def _on_playstate(self, playstate):
        if playstate is None:
            return
        self._playstate = playstate
        self._sync_control_icons()

    def _on_source(self, source):
        if source is None:
            return
        self._source = source
        self._sync_control_icons()

    def _on_nowplaying(self, playing):
        if playing is None:
            return
        name, title = Idle._extract_name_title(playing)

        haschange = False
        if name != self._playingname:
            self._playingname = name
            self._nameoffset = 0.0
            self._namewidth = int(Idle.font.getlength(name))
            haschange = True

        if title != self._playingtitle:
            self._playingtitle = title
            self._titleoffset = 0.0
            self._titlewidth = int(Idle.font.getlength(title))
            haschange = True

        if haschange:
            self.mark_dirty()

    def update(self, dt):
        if not self._active:
            return

        haschange = False

        nowminute = datetime.datetime.now().strftime("%H:%M")
        if nowminute != self._lastclockminute:
            self._lastclockminute = nowminute
            haschange = True

        if self._namewidth > 127:
            oldoffset = int(self._nameoffset)
            self._nameoffset += self._scroll_speed * dt
            maxoffset = (self._namewidth - 127) + self._scroll_gap
            if self._nameoffset > maxoffset:
                self._nameoffset = 0.0
            if int(self._nameoffset) != oldoffset:
                haschange = True

        if self._titlewidth > 127:
            oldoffset = int(self._titleoffset)
            self._titleoffset += self._scroll_speed * dt
            maxoffset = (self._titlewidth - 127) + self._scroll_gap
            if self._titleoffset > maxoffset:
                self._titleoffset = 0.0
            if int(self._titleoffset) != oldoffset:
                haschange = True

        if haschange:
            self.mark_dirty()


    def push_callback(self):
        if len(self._buttons) > 0:
            self._buttons[self._selectedbtnindex].trigger()

    def turn_callback(self, direction):
        if len(self._buttons) > 0:
            self._selectedbtnindex = (self._selectedbtnindex + direction) % len(self._buttons)
