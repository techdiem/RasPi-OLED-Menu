""" IDLE screen """
import datetime
from ui.windowbase import WindowBase
from ui.metabutton import MetaButton
from PIL import Image, ImageDraw, ImageFont
import settings

class Idle(WindowBase):
    clockfont = ImageFont.truetype(settings.FONT_CLOCK, size=28)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=12)
    widgeticon = ImageFont.truetype(settings.FONT_ICONS, size=14)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager, musicmanager)
        self._active = False
        self._display_width = getattr(self.device, "width", 128)
        self._display_height = getattr(self.device, "height", 64)
        self._text_area_width = self._display_width - 1
        self._base_image = Image.new("1", (self._display_width, self._display_height), 0)
        self._base_dirty = True
        self._playingname = ""
        self._playingtitle = ""
        self._nameoffset = 0.0
        self._titleoffset = 0.0
        self._namewidth = 0
        self._titlewidth = 0
        self._name_image = None
        self._title_image = None
        self._scroll_speed = 16.0
        self._scroll_gap = 20.0
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
        self._lastclockminute = ""
        self._base_dirty = True
        self.mark_dirty()

    def deactivate(self):
        self._active = False

    def render(self):
        if self._base_dirty:
            self._rebuild_base_image()

        frame = self._base_image.copy()
        self._paste_scrolling_text(frame, self._name_image, int(self._nameoffset), 23)
        self._paste_scrolling_text(frame, self._title_image, int(self._titleoffset), 35)
        self.device.display(frame)

    def _rebuild_base_image(self):
        image = Image.new("1", (self._display_width, self._display_height), 0)
        draw = ImageDraw.Draw(image)
        now = datetime.datetime.now()

        draw.text((1, 2), "\uf027", font=Idle.faicons, fill=1)
        draw.text((12, 2), f"{str(self._volume)}%", font=Idle.font, fill=1)
        draw.text((45, 4), self._widgeticon, font=Idle.widgeticon, fill=1)
        draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill=1)

        for button in self._buttons:
            draw.text((button.posx, button.posy), button.icon, font=Idle.faicons, fill=1)

        btn = self._buttons[self._selectedbtnindex]
        draw.line((btn.posx, btn.posy + 13, btn.posx + 11, btn.posy + 13), width=2, fill=1)

        self._base_image = image
        self._base_dirty = False

    def _paste_scrolling_text(self, frame, image, offset, y):
        if image is None:
            return

        x = 1 - offset
        if x >= self._display_width or y >= self._display_height:
            return

        src_left = max(-x, 0)
        src_top = 0
        src_right = min(image.width, self._display_width - x)
        src_bottom = min(image.height, self._display_height - y)

        if src_right <= src_left or src_bottom <= src_top:
            return

        crop = image.crop((src_left, src_top, src_right, src_bottom))
        frame.paste(crop, (max(x, 0), y))

    @staticmethod
    def _render_text_image(text, font):
        if not text:
            return None

        bbox = font.getbbox(text)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        image = Image.new("1", (width, height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((-bbox[0], -bbox[1]), text, font=font, fill=1)
        return image

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
        changed = False

        if not self._mopidy_connected:
            if self._widgeticon != "\uf071":
                self._widgeticon = "\uf071"
                changed = True
        elif self._source == "mpd" and self._playstate in ["play", "pause"]:
            if self._playstate == "play":
                playpauseicon = "\uf04c"
            else:
                playpauseicon = "\uf04b"
            showskipicons = True
            if self._widgeticon != "\ue585":
                self._widgeticon = "\ue585"
                changed = True
        elif self._source == "airplay":
            if self._widgeticon != "\uf3cd":
                self._widgeticon = "\uf3cd"
                changed = True
        else:
            if self._widgeticon != "":
                self._widgeticon = ""
                changed = True
        
        if playpauseicon != self._lastplaypauseicon:
            self._lastplaypauseicon = playpauseicon
            self._buttons[2].icon = playpauseicon
            if showskipicons:
                self._buttons[1].icon = "\uf04a"
                self._buttons[3].icon = "\uf04e"
            else:
                self._buttons[1].icon = ""
                self._buttons[3].icon = ""
            changed = True

        if changed:
            self._base_dirty = True
            self.mark_dirty()

    def _on_volume(self, volume):
        if volume is None:
            return
        if self._volume != volume:
            self._volume = volume
            self._base_dirty = True
            self.mark_dirty()

    def _on_mopidy_connection(self, connected):
        if connected is None:
            return
        if self._mopidy_connected != connected:
            self._mopidy_connected = connected
            self._base_dirty = True
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
            self._name_image = Idle._render_text_image(name, Idle.font)
            haschange = True

        if title != self._playingtitle:
            self._playingtitle = title
            self._titleoffset = 0.0
            self._titlewidth = int(Idle.font.getlength(title))
            self._title_image = Idle._render_text_image(title, Idle.font)
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
            self._base_dirty = True
            haschange = True

        if self._namewidth > self._text_area_width:
            oldoffset = int(self._nameoffset)
            self._nameoffset += self._scroll_speed * dt
            maxoffset = (self._namewidth - self._text_area_width) + self._scroll_gap
            if self._nameoffset > maxoffset:
                self._nameoffset = 0.0
            if int(self._nameoffset) != oldoffset:
                haschange = True

        if self._titlewidth > self._text_area_width:
            oldoffset = int(self._titleoffset)
            self._titleoffset += self._scroll_speed * dt
            maxoffset = (self._titlewidth - self._text_area_width) + self._scroll_gap
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
        self._base_dirty = True
        self.mark_dirty()
