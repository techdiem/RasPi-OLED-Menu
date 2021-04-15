""" Main menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Mainmenu(WindowBase):
    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0

    def render(self):
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

        with canvas(self.device) as draw:
            #rectangle as selection marker
            if self.counter < 3: #3 icons in one row
                y_coord = 2
                x_coord = 7 + self.counter * 35
            else:
                y_coord = 35
                x_coord = 6 + (self.counter - 3) * 35
            draw.rectangle((x_coord, y_coord, x_coord+25, y_coord+25), outline=255, fill=0)

            #icons as menu buttons
            draw.text((11, 6), text="\uf0a8", font=faicons, fill="white") #back
            draw.text((44, 6), text="\uf519", font=faicons, fill="white") #radio (old icon: f145)
            draw.text((83, 6), text="\uf1c7", font=faicons, fill="white") #playlists
            draw.text((10, 39), text="\uf011", font=faicons, fill="white") #shutdown

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("idle")
        elif self.counter == 1:
            self.windowmanager.set_window("radiomenu")
        elif self.counter == 2:
            self.windowmanager.set_window("playlistmenu")
        elif self.counter == 3:
            self.windowmanager.set_window("shutdownmenu")

    def turn_callback(self, direction):
        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction
