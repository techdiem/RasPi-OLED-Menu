""" Main menu """
from ui.windowbase import WindowBase
from ui.metabutton import MetaButton
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Mainmenu(WindowBase):
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self._buttons = []
        self._selectedbtnindex = 0

    def render(self):
        with canvas(self.device) as draw:
            #Menu buttons
            self._buttons.append(MetaButton(11, 6, "\uf0a8", lambda: self.windowmanager.set_window("idle"))) #back
            self._buttons.append(MetaButton(44, 6, "\uf519", lambda: self.windowmanager.set_window("radiomenu"))) #radio
            self._buttons.append(MetaButton(83, 6, "\uf1c7", lambda: self.windowmanager.set_window("playlistmenu"))) #playlists
            self._buttons.append(MetaButton(10, 39, "\uf011", lambda: self.windowmanager.set_window("shutdownmenu"))) #shutdown

            #rectangle as selection marker
            btn = self._buttons[self._selectedbtnindex]
            draw.rectangle((btn.posx-4, btn.posy-4, btn.posx+21, btn.posy+21), outline=255, fill=0)

            #Draw buttons
            for button in self._buttons:
                draw.text((button.posx, button.posy), button.icon, font=Mainmenu.faicons, fill="white")

    def push_callback(self):
        self._buttons[self._selectedbtnindex].trigger()

    def turn_callback(self, direction):
        if self._selectedbtnindex + direction <= len(self._buttons)-1 and \
            self._selectedbtnindex + direction >= 0:
            self._selectedbtnindex += direction