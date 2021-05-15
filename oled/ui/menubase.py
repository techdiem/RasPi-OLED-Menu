""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class MenuBase(WindowBase):
    def __init__(self, windowmanager, title):
        super().__init__(windowmanager)
        self.counter = 0
        self.page = 0
        self.menu = []
        self.title = title

    def render(self):
        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=11)
        with canvas(self.device) as draw:
            #Back button and selection arrow
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=faicons, fill="white")
            else:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                #Selection arrow
                draw.polygon(((1, 7+self.counter*12), (1, 11+self.counter*12),
                                        (5, 9+self.counter*12)), fill="white")

            #Calculate title coordinate from text lenght
            draw.text(((128-len(self.title)*5)/2, 1), text=self.title, font=font, fill="white")

            #Playlists
            for i in range(4 if len(self.menu) >= 4 else len(self.menu)):
                draw.text((8, 17+i*12), text=self.menu[i+self.page], font=font, fill="white")



    def push_callback(self):
        raise NotImplementedError()

    def turn_callback(self, direction):
        if self.counter + direction >= 0:
            #first 4 items in long menu
            if len(self.menu) > 4 and self.counter + direction <= 4 and self.page == 0:
                self.counter += direction
            #other items in long menu
            elif len(self.menu) > 4 and self.page + direction + 4 <= len(self.menu):
                self.page += direction
            #short menu < 4 items
            elif len(self.menu) <= 4 and self.counter + direction <= len(self.menu):
                self.counter += direction
