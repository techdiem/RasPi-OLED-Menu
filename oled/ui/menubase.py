""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class MenuBase(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=11)

    def __init__(self, windowmanager, musicmanager, title):
        super().__init__(windowmanager, musicmanager)
        self.counter = 0
        self.page = 0
        self.menu = []
        self.title = title
        self.mark_dirty()

    def render(self):
        with canvas(self.device) as draw:
            #Back button and selection arrow
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=MenuBase.faicons, fill="white")
            else:
                draw.text((1, 1), text="\uf104", font=MenuBase.faicons, fill="white")
                #Selection arrow
                draw.polygon(((1, 7+self.counter*12), (1, 11+self.counter*12),
                                        (5, 9+self.counter*12)), fill="white")

            #Calculate title coordinate from text lenght
            draw.text(((128-len(self.title)*5)/2, 1), text=self.title,
                       font=MenuBase.font, fill="white")

            #Menu entries
            for i in range(4 if len(self.menu) >= 4 else len(self.menu)):
                draw.text((8, 17+i*12), text=self.get_menu_text(self.menu[i+self.page]),
                          font=MenuBase.font, fill="white")

    def push_callback(self):
        raise NotImplementedError()

    def get_menu_text(self, item):
        return str(item)

    def turn_callback(self, direction):
        changed = False
        if self.counter + direction >= 0:
            #first 4 items in long menu
            if len(self.menu) > 4 and self.counter + direction <= 4 and self.page == 0:
                self.counter += direction
                changed = True
            #other items in long menu
            elif len(self.menu) > 4 and self.page + direction + 4 <= len(self.menu):
                self.page += direction
                changed = True
            #short menu < 4 items
            elif len(self.menu) <= 4 and self.counter + direction <= len(self.menu):
                self.counter += direction
                changed = True

        if changed:
            self.mark_dirty()
