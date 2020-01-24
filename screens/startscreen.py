from PIL import ImageFont
from luma.core.render import canvas
from setupHandler import font_icons, font_text

#Functions for startscreen
def draw(device):
    with canvas(device) as draw:
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=35)

        draw.text((25, 3), text="Wird gestartet...", font=font, fill="white")
        draw.text((50, 25), text="\uf251", font=fontawesome, fill="white")