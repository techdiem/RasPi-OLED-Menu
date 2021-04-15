""" IDLE screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Idle(WindowBase):
    def __init__(self, windowmanager, mopidyconnection, shairportconnection):
        super().__init__(windowmanager)
        self.counter = 0

    def render(self):
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

        with canvas(self.device) as draw:
            pass

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")

    def turn_callback(self, direction):
        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction

    def airplay_callback(self, info, nowplaying):
        pass
