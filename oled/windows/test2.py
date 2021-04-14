""" Test screen """
from ui.windowbase import WindowBase

class Test2(WindowBase):
    def render(self):
        with self.canvas as draw:
            draw.rectangle((10, 30, 10+25, 30+25), outline=255, fill=0)

    def push_callback(self):
        self.windowmanager.set_window("test")

    def turn_callback(self, direction):
        print("Turn", direction)
