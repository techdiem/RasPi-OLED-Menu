""" Test screen """
from ui.window import Window

class TestView(Window):
    def render(self):
        with self.canvas as draw:
            draw.rectangle((5, 2, 5+25, 2+25), outline=255, fill=0)
