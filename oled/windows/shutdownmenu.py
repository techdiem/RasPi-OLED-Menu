""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Shutdownmenu(WindowBase):
    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0

    def render(self):
        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

        with canvas(self.device) as draw:
            draw.text((5, 2), text="Wirklich ausschalten?", font=font, fill="white")
            if self.counter == 0:
                x = 10
                y = 22
            elif self.counter == 1:
                x = 47
                y = 22
            else:
                x = 89
                y = 22
            draw.rectangle((x, y, x+30, y+40), outline=255, fill=0)

            draw.text((13, 25), text="Nein", font=font, fill="white")
            draw.text((15, 40), text="\uf0a8", font=faicons, fill="white")

            draw.text((56, 25), text="Ja", font=font, fill="white")
            draw.text((55, 40), text="\uf011", font=faicons, fill="white")

            draw.text((92, 25), text="DSP", font=font, fill="white")
            draw.text((94, 40), text="\uf108", font=faicons, fill="white")

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            pass
            #TODO Shutdown system function
        elif self.counter == 2:
            self.windowmanager.clear_window()

    def turn_callback(self, direction):
        if self.counter + direction <= 2 and self.counter + direction >= 0:
            self.counter += direction
