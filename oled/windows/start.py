""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Start(WindowBase):
    def render(self):
        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=35)

        with canvas(self.device) as draw:
            draw.text((25, 3), text="Wird gestartet...", font=font, fill="white")
            draw.text((50, 25), text="\uf251", font=fontawesome, fill="white")

    def push_callback(self):
        pass

    def turn_callback(self, direction):
        pass