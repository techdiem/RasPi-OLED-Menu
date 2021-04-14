""" Empty display """
from ui.windowbase import WindowBase

class Blank(WindowBase):
    def render(self):
        pass

    def turn_callback(self, direction):
        pass

    def push_callback(self):
        #Wake from sleep mode
        self.windowmanager.device.show()
        self.windowmanager.set_window("test")
