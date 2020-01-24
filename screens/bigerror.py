from PIL import ImageFont
from luma.core.render import canvas
from setupHandler import font_icons, font_text

#Error message on screen
def draw(device, message):
    global font_text, font_icons
    with canvas(device) as draw:
        font = ImageFont.truetype(font_text, size=12)
        fontawesome = ImageFont.truetype(font_icons, size=35)

        if len(message) > 23:
            draw.text((5, 3), text=message[0:23], font=font, fill="white")
            draw.text((5, 12), text=message[23:], font=font, fill="white")
        else:
            draw.text((5, 3), text=message, font=font, fill="white")
        draw.text((50, 28), text="\uf071", font=fontawesome, fill="white")