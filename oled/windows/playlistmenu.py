""" Playlist menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Playlistmenu(WindowBase):
    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.page = 0
        self.menu = ["abc", "def"]

    def render(self):
        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=11)
        with canvas(self.device) as draw:
            #Header
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=faicons, fill="white")
            else:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                #Selection arrow
                draw.polygon(((1, 7+self.counter*12), (1, 11+self.counter*12), (5, 9+self.counter*12)), fill="white")

            draw.text((42, 1), text="Playlists", font=faicons, fill="white")

            #Playlists
            draw.text((8, 18), text="Text1", font=font, fill="white")
            draw.text((8, 30), text="Text2", font=font, fill="white")
            draw.text((8, 42), text="Text3", font=font, fill="white")
            draw.text((8, 54), text="Text4", font=font, fill="white")



    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            #TODO load playlist
            self.windowmanager.set_window("idle")

    def turn_callback(self, direction):
        if self.counter + direction <= 4 and self.counter + direction >= 0:
            self.counter += direction
