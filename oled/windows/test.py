""" Test screen """
from ui.windowbase import WindowBase

class Test(WindowBase):
    def render(self):
        with self.canvas as draw:
            draw.rectangle((5, 2, 5+25, 2+25), outline=255, fill=0)

    def push_callback(self):
        self.windowmanager.clear_window()

    def turn_callback(self, direction):
        print("Turn", direction)
